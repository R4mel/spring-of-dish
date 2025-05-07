// src/contexts/AuthContext.jsx
import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext({
  token: null,
  login: (token) => {},
  logout: () => {},
});

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);

  // 새로고침할 때 localStorage에 남아있는 토큰 복원
  useEffect(() => {
    const saved = localStorage.getItem('access_token');
    if (saved) setToken(saved);
  }, []);

  const login = (newToken) => {
    setToken(newToken);
    localStorage.setItem('access_token', newToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('access_token');
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}