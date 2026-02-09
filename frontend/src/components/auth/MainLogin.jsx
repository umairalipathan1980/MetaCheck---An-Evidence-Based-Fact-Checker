import { useState } from 'react'

import { Button } from '../ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'
import { Input } from '../ui/input'
import { useAuth } from '../../contexts/AuthContext'

export function MainLogin() {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    const result = await login(username, password)
    setLoading(false)
    if (!result.success) {
      setError(result.error || 'Login failed')
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden">
      <div className="pointer-events-none absolute inset-0 bg-grid-radial opacity-60" aria-hidden="true" />
      <div className="relative z-10 flex min-h-screen items-center justify-center px-4">
        <Card className="w-full max-w-2xl border-slate-200 bg-white shadow-[0_30px_60px_rgba(15,23,42,0.12)]">
          <CardHeader>
            <div className="mb-3 flex justify-center">
              <img
                src="/metacheck-logo.png"
                alt="MetaCheck"
                className="w-full max-w-md"
              />
            </div>
            <CardTitle>Main Login</CardTitle>
            <CardDescription>Sign in to access MetaCheck AI Analysis.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Username</label>
                <Input
                  type="text"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  placeholder="Enter username"
                  required
                  autoFocus
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700">Password</label>
                <Input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
              {error && (
                <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                  {error}
                </div>
              )}
              <Button type="submit" disabled={loading || !username || !password} className="w-full">
                {loading ? 'Signing in...' : 'Sign in'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
