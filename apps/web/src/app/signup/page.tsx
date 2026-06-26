'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/store/AuthContext'

export default function SignupPage() {
  const router = useRouter()
  const { signup } = useAuth()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password.length < 8) { 
      setError('Password must be at least 8 characters')
      return 
    }
    setError('')
    setLoading(true)
    try {
      await signup(email, password, name)
      router.push('/profile')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Signup failed. Please try again.')
    } finally { 
      setLoading(false) 
    }
  }

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center relative overflow-hidden">
      {/* Background Decorative Elements */}
      <div className="absolute top-[-10%] left-[-5%] w-[600px] h-[600px] bg-primary/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-5%] w-[500px] h-[500px] bg-secondary/20 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-md relative z-10 px-4 py-12">
        {/* Back Button */}
        <Link 
          href="/" 
          className="inline-flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors mb-8 font-label-lg"
        >
          <span className="material-symbols-outlined text-sm">arrow_back</span>
          Back to Home
        </Link>

        {/* Glassmorphic Card */}
        <div className="bg-surface-container-lowest/80 dark:bg-inverse-surface/80 backdrop-blur-3xl border border-white/20 shadow-[0_8px_40px_rgba(43,76,190,0.08)] rounded-3xl p-8 md:p-10">
          
          <div className="text-center mb-10">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary/10 mb-6">
              <span className="material-symbols-outlined text-primary text-4xl" style={{ fontVariationSettings: "'FILL' 1" }}>person_add</span>
            </div>
            <h1 className="font-display-sm text-display-sm text-primary mb-2">Create Account</h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant">Save places, track history, and more</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="font-label-md text-label-md text-on-surface block mb-2" htmlFor="name">Name (Optional)</label>
              <input 
                id="name" 
                type="text" 
                className="w-full h-[56px] px-4 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-on-surface placeholder:text-on-surface-variant/50" 
                placeholder="Your name" 
                value={name} 
                onChange={e => setName(e.target.value)} 
              />
            </div>

            <div>
              <label className="font-label-md text-label-md text-on-surface block mb-2" htmlFor="email">Email</label>
              <input 
                id="email" 
                type="email" 
                className="w-full h-[56px] px-4 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-on-surface placeholder:text-on-surface-variant/50" 
                placeholder="you@example.com" 
                value={email} 
                onChange={e => setEmail(e.target.value)} 
                required 
              />
            </div>
            
            <div>
              <label className="font-label-md text-label-md text-on-surface block mb-2" htmlFor="password">Password</label>
              <input 
                id="password" 
                type="password" 
                className="w-full h-[56px] px-4 rounded-xl border border-outline-variant bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all text-on-surface placeholder:text-on-surface-variant/50" 
                placeholder="Min. 8 characters" 
                value={password} 
                onChange={e => setPassword(e.target.value)} 
                required 
                minLength={8}
              />
            </div>

            {error && (
              <div className="flex items-start gap-3 p-4 bg-error-container/20 border border-error/20 rounded-xl">
                <span className="material-symbols-outlined text-error text-sm mt-0.5">error</span>
                <p className="text-error font-body-sm text-body-sm">{error}</p>
              </div>
            )}

            <button 
              type="submit" 
              disabled={loading} 
              className="w-full h-[56px] flex items-center justify-center gap-2 bg-primary text-white rounded-xl font-label-lg text-label-lg shadow-lg shadow-primary/25 hover:shadow-primary/40 hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:hover:translate-y-0 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <span className="material-symbols-outlined animate-spin text-sm">progress_activity</span>
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          <div className="mt-8 pt-8 border-t border-outline-variant/30 text-center space-y-4">
            <p className="font-body-md text-body-md text-on-surface-variant">
              Already have an account?{' '}
              <Link href="/login" className="text-primary font-bold hover:underline transition-all">Sign In</Link>
            </p>
            <Link href="/" className="inline-flex items-center gap-1 font-label-sm text-label-sm text-on-surface-variant hover:text-primary transition-colors">
              Continue as guest 
              <span className="material-symbols-outlined text-sm">arrow_forward</span>
            </Link>
          </div>
          
          <p className="text-center font-label-sm text-[11px] text-on-surface-variant mt-6 leading-relaxed opacity-70">
            By signing up, you agree that we store only your email for authentication. No medical data is stored.
          </p>

        </div>
      </div>
    </div>
  )
}
