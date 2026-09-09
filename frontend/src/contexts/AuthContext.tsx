import React, { createContext, useContext, useState, useEffect } from 'react';

export type Role = 'ADMIN' | 'MAINTAINER' | null;

interface AuthContextType {
  role: Role;
  login: (role: Role) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRole] = useState<Role>(null);

  useEffect(() => {
    const savedRole = localStorage.getItem('veda-demo-role') as Role;
    if (savedRole === 'ADMIN' || savedRole === 'MAINTAINER') {
      setRole(savedRole);
    }
  }, []);

  const login = (newRole: Role) => {
    setRole(newRole);
    if (newRole) {
      localStorage.setItem('veda-demo-role', newRole);
    }
  };

  const logout = () => {
    setRole(null);
    localStorage.removeItem('veda-demo-role');
  };

  return (
    <AuthContext.Provider value={{ role, login, logout, isAuthenticated: !!role }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
