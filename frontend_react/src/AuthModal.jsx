import React, { useState } from 'react'
import { supabase } from './supabaseClient'

export default function AuthModal({ onAuthenticated }) {
  const [mode, setMode] = useState('login') // 'login' or 'signup'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleSubmit = async () => {
    setError('')
    setMessage('')
    setLoading(true)

    try {
      if (mode === 'signup') {
        const { error } = await supabase.auth.signUp({ email, password })
        if (error) throw error
        setMessage('Check your email to confirm your account.')
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
        onAuthenticated(data.session)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(11, 10, 8, 0.95)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999
    }}>
      <div style={{
        backgroundColor: '#0b0a08',
        border: '1px solid #c9a961',
        borderRadius: '12px',
        padding: '40px',
        width: '100%',
        maxWidth: '400px',
        fontFamily: 'DM Sans, sans-serif'
      }}>
        <h2 style={{
          fontFamily: 'Cormorant Garamond, serif',
          color: '#c9a961',
          fontSize: '28px',
          marginBottom: '8px',
          textAlign: 'center'
        }}>
          VigilAI
        </h2>
        <p style={{
          color: '#888',
          fontSize: '13px',
          textAlign: 'center',
          marginBottom: '32px'
        }}>
          {mode === 'login' ? 'Sign in to your account' : 'Create a new account'}
        </p>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          style={{
            width: '100%',
            padding: '12px',
            marginBottom: '12px',
            backgroundColor: '#1a1914',
            border: '1px solid #333',
            borderRadius: '6px',
            color: '#fff',
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '14px',
            boxSizing: 'border-box'
          }}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          style={{
            width: '100%',
            padding: '12px',
            marginBottom: '20px',
            backgroundColor: '#1a1914',
            border: '1px solid #333',
            borderRadius: '6px',
            color: '#fff',
            fontFamily: 'DM Sans, sans-serif',
            fontSize: '14px',
            boxSizing: 'border-box'
          }}
        />

        {error && (
          <p style={{ color: '#ff4d4d', fontSize: '13px', marginBottom: '12px' }}>
            {error}
          </p>
        )}

        {message && (
          <p style={{ color: '#c9a961', fontSize: '13px', marginBottom: '12px' }}>
            {message}
          </p>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            width: '100%',
            padding: '12px',
            backgroundColor: '#c9a961',
            color: '#0b0a08',
            border: 'none',
            borderRadius: '6px',
            fontFamily: 'DM Sans, sans-serif',
            fontWeight: '700',
            fontSize: '14px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
            marginBottom: '16px'
          }}
        >
          {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Sign Up'}
        </button>

        <p style={{
          color: '#888',
          fontSize: '13px',
          textAlign: 'center',
          cursor: 'pointer'
        }}
          onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setError(''); setMessage('') }}
        >
          {mode === 'login'
            ? "Don't have an account? Sign up"
            : 'Already have an account? Sign in'}
        </p>
      </div>
    </div>
  )
}
