import os
import json
import pickle
import numpy as np
import pandas as pd
import xgboost as xgb
import tensorflow as tf

from agents.orchestration.schemas import VehicleOrchestrationRequest

class MLInferenceService:
    def __init__(self):
        self._load_tank_artifacts()
        self._load_logistic_officer_artifacts()

    def _load_tank_artifacts(self):
        rf_dir = r"d:\VEDA\ml\tank\random_forest\VEDA_Tank_RF_Phase4_Output"
        with open(os.path.join(rf_dir, "RF_phase4_model.pkl"), "rb") as f:
            self.tank_rf_model = pickle.load(f)
        with open(os.path.join(rf_dir, "RF_phase4_risk_threshold.pkl"), "rb") as f:
            self.tank_rf_threshold = float(pickle.load(f))
        with open(os.path.join(rf_dir, "RF_phase4_feature_columns.pkl"), "rb") as f:
            self.tank_rf_features = pickle.load(f)
            
        lstm_dir = r"d:\VEDA\ml\tank\lstm_1dcnn\Model 2 Current Best"
        with open(os.path.join(lstm_dir, "feature_scaler_train_only.pkl"), "rb") as f:
            self.tank_lstm_scaler = pickle.load(f)
            
        self._apply_keras_patch()
        self.tank_lstm_model = tf.keras.models.load_model(os.path.join(lstm_dir, "VEDA_Phase5B_LSTM_1DCNN_final.keras"))
        
        xgb_dir = r"d:\VEDA\ml\tank\xgboost\VEDA_Tank_XGB_Phase3_Output"
        self.tank_xgb_model = xgb.XGBRegressor()
        self.tank_xgb_model.load_model(os.path.join(xgb_dir, "veda_tank_xgboost_model.json"))
        
        # We know downstream features for LSTM is 45. (RF 43 features + 2 RF outputs)
        with open(os.path.join(r"d:\VEDA\datasets\tank\downstream", "downstream_feature_columns.json"), "r") as f:
            self.tank_lstm_features = json.load(f)

    def _load_logistic_officer_artifacts(self):
        rf_dir = r"d:\VEDA\ml\logistic_officer\random_forest\VEDA_Logistic_Officer_RF_Phase1_V2_Output"
        with open(os.path.join(rf_dir, "RF_phase1_v2_model.pkl"), "rb") as f:
            self.lo_rf_model = pickle.load(f)
        with open(os.path.join(rf_dir, "RF_phase1_v2_risk_threshold.json"), "r") as f:
            self.lo_rf_threshold = json.load(f)["risk_threshold"]
        with open(os.path.join(rf_dir, "RF_phase1_v2_feature_columns.json"), "r") as f:
            self.lo_rf_features = json.load(f)
            
        lstm_dir = r"d:\VEDA\ml\logistic_officer\lstm_1dcnn\VEDA_Logistic_Officer_LSTM_1DCNN_Phase2_V2_Output"
        with open(os.path.join(lstm_dir, "feature_scaler_train_only.pkl"), "rb") as f:
            self.lo_lstm_scaler = pickle.load(f)
        with open(os.path.join(lstm_dir, "LSTM_1DCNN_phase2_v2_feature_columns.json"), "r") as f:
            self.lo_lstm_features = json.load(f)
            
        self._apply_keras_patch()
        self.lo_lstm_model = tf.keras.models.load_model(os.path.join(lstm_dir, "VEDA_Logistic_Officer_LSTM_1DCNN_V2_final.keras"))
        
        xgb_dir = r"d:\VEDA\ml\logistic_officer\xgboost\VEDA_Logistic_Officer_XGB_Phase3_V2_Output"
        self.lo_xgb_model = xgb.XGBRegressor()
        self.lo_xgb_model.load_model(os.path.join(xgb_dir, "VEDA_Logistic_Officer_XGB_Phase3_V2_model.json"))

    def _apply_keras_patch(self):
        if hasattr(self, "_keras_patched"):
            return
        original_dense_from_config = tf.keras.layers.Dense.from_config
        def custom_dense_from_config(cls, config):
            if 'quantization_config' in config:
                del config['quantization_config']
            return original_dense_from_config(config)
        tf.keras.layers.Dense.from_config = classmethod(custom_dense_from_config)

        original_conv1d_from_config = tf.keras.layers.Conv1D.from_config
        def custom_conv1d_from_config(cls, config):
            if 'quantization_config' in config:
                del config['quantization_config']
            return original_conv1d_from_config(config)
        tf.keras.layers.Conv1D.from_config = classmethod(custom_conv1d_from_config)

        original_lstm_from_config = tf.keras.layers.LSTM.from_config
        def custom_lstm_from_config(cls, config):
            if 'quantization_config' in config:
                del config['quantization_config']
            return original_lstm_from_config(config)
        tf.keras.layers.LSTM.from_config = classmethod(custom_lstm_from_config)
        self._keras_patched = True

    def _preprocess_tank(self, df: pd.DataFrame):
        df = df.copy()
        
        if 'Coolant_Ambient_Delta' not in df.columns:
            df['Coolant_Ambient_Delta'] = df['Coolant_Temp_C'] - df['Ambient_Temp_C']
            df['Oil_Ambient_Delta'] = df['Oil_Temp_C'] - df['Ambient_Temp_C']
            df['Exhaust_Ambient_Delta'] = df['Exhaust_Gas_Temp_C'] - df['Ambient_Temp_C']
            df['Load_RPM_Ratio'] = df['Engine_Load_pct'] / (df['Engine_RPM'] + 1e-6)
            df['Odometer_per_Hour'] = df['Odometer_km'] / (df['Operating_Hours'] + 1e-6)
            df['BrakeWear_per_Hour'] = df['Brake_Pad_Wear_pct'] / (df['Operating_Hours'] + 1e-6)
            
            # rolling 10
            rolling_cols = ['Engine_Load_pct', 'Engine_RPM', 'Coolant_Temp_C', 'Oil_Pressure_bar', 'Engine_Vibration_mm_s', 'Brake_Pad_Wear_pct', 'Fuel_Level_pct']
            for col in rolling_cols:
                df[f'{col}_past_mean10'] = df[col].rolling(10, min_periods=1).mean()
                df[f'{col}_past_std10'] = df[col].rolling(10, min_periods=1).std().fillna(0)
                
            delta_cols = ['Coolant_Temp_C', 'Oil_Temp_C', 'Oil_Pressure_bar', 'Engine_Vibration_mm_s', 'Brake_Pad_Wear_pct']
            for col in delta_cols:
                df[f'{col}_delta1'] = df[col].diff(1).fillna(0)
                
        return df

    def run_inference(self, vehicle_id: str, vehicle_class: str, telemetry_df: pd.DataFrame) -> VehicleOrchestrationRequest:
        if telemetry_df is None or len(telemetry_df) == 0:
            return VehicleOrchestrationRequest(
                vehicle_id=vehicle_id,
                vehicle_class=vehicle_class,
                telemetry=None
            )
            
        is_tank = vehicle_class.upper() == "TANK"
        
        # Get the latest raw telemetry for downstream agent processing
        latest_row_raw = telemetry_df.iloc[-1].to_dict()
        latest_row = {k: float(v) for k, v in latest_row_raw.items() if isinstance(v, (int, float, np.number)) and not pd.isna(v)}
        
        # Preprocessing
        if is_tank:
            df_proc = self._preprocess_tank(telemetry_df)
            rf_features_list = self.tank_rf_features
            rf_model = self.tank_rf_model
            rf_threshold = self.tank_rf_threshold
        else:
            df_proc = telemetry_df.copy()
            rf_features_list = self.lo_rf_features
            rf_model = self.lo_rf_model
            rf_threshold = self.lo_rf_threshold
            
        # Verify feature existence for RF
        missing_rf = [f for f in rf_features_list if f not in df_proc.columns]
        if missing_rf:
            raise ValueError(f"Missing RF features: {missing_rf}")
            
        # Run RF on the entire dataframe to get predictions for all timesteps (needed for LSTM)
        X_rf = df_proc[rf_features_list].copy()
        rf_probs = rf_model.predict_proba(X_rf)[:, 1]
        rf_preds = (rf_probs >= rf_threshold).astype(int)
        
        df_proc['RF_Abnormal_Probability'] = rf_probs
        df_proc['RF_Abnormal_Prediction'] = rf_preds
        # tank dataset uses "RF_Prediction", but LO uses "RF_Abnormal_Prediction"
        if is_tank:
            df_proc['RF_Prediction'] = rf_preds
            
        # Select latest RF stats for the response
        latest_rf_prob = float(rf_probs[-1])
        latest_rf_pred = int(rf_preds[-1])
        latest_rf_class = "abnormal" if latest_rf_pred == 1 else "normal"
        
        # Sequence building for LSTM/XGB
        if len(df_proc) < 30:
            return VehicleOrchestrationRequest(
                vehicle_id=vehicle_id,
                vehicle_class=vehicle_class,
                telemetry=latest_row,
                rf_abnormal_class=latest_rf_class,
                rf_abnormal_probability=latest_rf_prob,
                rf_abnormal_prediction=latest_rf_pred,
                lstm_rul_hours=None,
                xgb_rul_hours=None,
                fusion_rul_hours=None
            )
            
        seq_df = df_proc.iloc[-30:].copy()
        
        if is_tank:
            lstm_features_list = self.tank_lstm_features
            scaler = self.tank_lstm_scaler
            lstm_model = self.tank_lstm_model
            xgb_model = self.tank_xgb_model
            input_features = lstm_features_list
        else:
            lstm_features_list = self.lo_lstm_features
            scaler = self.lo_lstm_scaler
            lstm_model = self.lo_lstm_model
            xgb_model = self.lo_xgb_model
            input_features = scaler.feature_names_in_
            
        missing_lstm = [f for f in input_features if f not in seq_df.columns]
        if missing_lstm:
            raise ValueError(f"Missing LSTM/XGB features: {missing_lstm}")
            
        X_seq = seq_df[input_features].copy()
        
        if is_tank:
            # Tank uses StandardScaler which takes 2D
            X_scaled = scaler.transform(X_seq)
        else:
            # L/O uses ColumnTransformer
            X_scaled = scaler.transform(X_seq)
            
        # LSTM input shape (1, 30, num_features)
        X_lstm = X_scaled.reshape(1, 30, -1).astype(np.float32)
        
        # XGB input shape (1, 30 * num_features)
        X_xgb = X_scaled.flatten().reshape(1, -1)
        
        lstm_rul = float(lstm_model.predict(X_lstm, verbose=0)[0][0])
        xgb_rul = float(xgb_model.predict(X_xgb)[0])
        
        # Fusion
        if is_tank:
            # Phase 5C formula: 0.00 * LSTM + 1.00 * XGB
            fusion_rul = xgb_rul
        else:
            # Phase 4 V2 formula: 0.30 * LSTM + 0.70 * XGB
            fusion_rul = 0.30 * lstm_rul + 0.70 * xgb_rul
            
        return VehicleOrchestrationRequest(
            vehicle_id=vehicle_id,
            vehicle_class=vehicle_class,
            telemetry=latest_row,
            rf_abnormal_class=latest_rf_class,
            rf_abnormal_probability=latest_rf_prob,
            rf_abnormal_prediction=latest_rf_pred,
            lstm_rul_hours=lstm_rul,
            xgb_rul_hours=xgb_rul,
            fusion_rul_hours=fusion_rul
        )

# For testing
if __name__ == "__main__":
    service = MLInferenceService()
    print("Service initialized successfully.")
