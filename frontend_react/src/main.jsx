import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import AuthModal from './AuthModal'
import { supabase } from './supabaseClient'
import './index.css'

function Root() {
  const [session, setSession] = useState(undefined) // undefined = loading

  useEffect(() => {
    // Get current session on load
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
    })

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })

    return () => subscription.unsubscribe()
  }, [])

  // Still checking session
  if (session === undefined) {
    return (
      <div style={{
        backgroundColor: '#0b0a08',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'Cormorant Garamond, serif',
        color: '#c9a961',
        fontSize: '24px'
      }}>
        Loading...
      </div>
    )
  }

  // Not logged in — show modal
  if (!session) {
    return <AuthModal onAuthenticated={(session) => setSession(session)} />
  }

  // Logged in — show dashboard
  return <App session={session} onSignOut={() => setSession(null)} />
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>
)
