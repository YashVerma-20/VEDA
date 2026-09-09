"""
DUMMY / DEMONSTRATION FLEET READINESS POLICY CONFIGURATION
==========================================================
DISCLAIMER: 
These policies are NOT official military policies, BISAG-N policies,
Army policies, defence policies, or organizational readiness standards.
They are project-level demonstration policies created because no approved
organizational fleet-readiness policy was provided to the project.
"""

# Policy Version
FLEET_READINESS_POLICY_VERSION = "demo_v1"

# Vehicle-level thresholds (Dummy / Demonstration Values)
# RUL thresholds
RUL_NOT_READY_THRESHOLD = 100.0  # hours (Exclusive for ATTENTION, inclusive for NOT_READY)
RUL_ATTENTION_THRESHOLD = 300.0  # hours (Exclusive for READY, inclusive for ATTENTION)

# Fleet-level thresholds (Dummy / Demonstration Values)
FLEET_NOT_READY_PERCENTAGE = 30.0  # %
FLEET_NOT_READY_COUNT = 3

FLEET_READY_PERCENTAGE = 80.0  # %
FLEET_UNKNOWN_PERCENTAGE = 10.0  # %
FLEET_ATTENTION_PERCENTAGE = 20.0  # %
