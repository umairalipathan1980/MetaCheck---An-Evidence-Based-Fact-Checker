/**
 * Authentication context for managing admin login state.
 *
 * Provides authentication state and methods (login, logout, checkAuthStatus)
 * to all components in the application.
 */

import { createContext, useContext, useState, useEffect } from 'react'
import { getAuthStatus, postLogin, postLogout } from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState({
    isAuthenticated: false,
    username: null,
    loading: true
  })

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const { authenticated, username } = await getAuthStatus()
      setAuth({ isAuthenticated: authenticated, username, loading: false })
    } catch (error) {
      setAuth({ isAuthenticated: false, username: null, loading: false })
    }
  }

  const login = async (username, password) => {
    try {
      const result = await postLogin(username, password)
      setAuth({ isAuthenticated: true, username: result.username, loading: false })
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' }
    }
  }

  const logout = async () => {
    try {
      await postLogout()
      setAuth({ isAuthenticated: false, username: null, loading: false })
    } catch (error) {
      // Clear state anyway
      setAuth({ isAuthenticated: false, username: null, loading: false })
    }
  }

  return (
    <AuthContext.Provider value={{ ...auth, login, logout, checkAuthStatus }}>
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
