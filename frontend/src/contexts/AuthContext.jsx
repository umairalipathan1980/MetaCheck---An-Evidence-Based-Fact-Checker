/**
 * Authentication context for managing user/admin login state.
 *
 * Provides authentication state and methods (login, logout, checkAuthStatus)
 * to all components in the application.
 */

import { createContext, useContext, useState, useEffect } from 'react'
import { getAuthStatus, postAdminLogin, postLogin, postLogout } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState({
    isAuthenticated: false,
    username: null,
    role: null,
    loading: true
  })

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const { authenticated, username, role } = await getAuthStatus()
      setAuth({ isAuthenticated: authenticated, username, role, loading: false })
    } catch (error) {
      setAuth({ isAuthenticated: false, username: null, role: null, loading: false })
    }
  }

  const login = async (username, password) => {
    try {
      const result = await postLogin(username, password)
      setAuth({
        isAuthenticated: true,
        username: result.username,
        role: result.role || null,
        loading: false
      })
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' }
    }
  }

  const loginAdmin = async (username, password) => {
    try {
      const result = await postAdminLogin(username, password)
      setAuth({
        isAuthenticated: true,
        username: result.username,
        role: 'admin',
        loading: false
      })
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Admin login failed' }
    }
  }

  const logout = async () => {
    try {
      await postLogout()
      setAuth({ isAuthenticated: false, username: null, role: null, loading: false })
    } catch (error) {
      // Clear state anyway
      setAuth({ isAuthenticated: false, username: null, role: null, loading: false })
    }
  }

  return (
    <AuthContext.Provider value={{ ...auth, login, loginAdmin, logout, checkAuthStatus }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
