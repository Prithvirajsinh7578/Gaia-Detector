import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { loginUser } from '../../services/api';
import { HiOutlineMail, HiOutlineLockClosed, HiOutlineCheckCircle, HiOutlineExclamationCircle } from 'react-icons/hi';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState(null); // 'submitting' | 'success' | 'error'
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setStatus('error');
      setMessage('Please enter both email and password.');
      return;
    }
    setStatus('submitting');
    try {
      await loginUser(email, password);
      setStatus('success');
      setMessage('Signed in successfully! Redirecting to workbench...');
      setTimeout(() => navigate('/upload'), 1200);
    } catch (err) {
      setStatus('error');
      setMessage(err.message || 'Login failed. Please verify credentials.');
    }
  };

  return (
    <div className="min-h-screen pt-32 pb-16 px-4 flex items-center justify-center">
      <div className="w-full max-w-md glass rounded-3xl p-8 border border-white/10 shadow-2xl">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-white mb-2 font-heading">
            Welcome <span className="bg-gradient-to-r from-primary-cyan to-primary-purple bg-clip-text text-transparent">Back</span>
          </h2>
          <p className="text-gray-400 text-xs">
            Sign in to access your Gaia Detector history and preferences.
          </p>
        </div>

        {status === 'success' && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
            <HiOutlineCheckCircle className="w-5 h-5 shrink-0" />
            <span>{message}</span>
          </div>
        )}

        {status === 'error' && (
          <div className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs flex items-center gap-2">
            <HiOutlineExclamationCircle className="w-5 h-5 shrink-0" />
            <span>{message}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-gray-300 text-xs font-semibold block mb-1.5">Email Address</label>
            <div className="relative">
              <HiOutlineMail className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-white text-sm focus:outline-none focus:border-primary-cyan transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="text-gray-300 text-xs font-semibold block mb-1.5">Password</label>
            <div className="relative">
              <HiOutlineLockClosed className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-white text-sm focus:outline-none focus:border-primary-cyan transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={status === 'submitting'}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-primary-cyan to-primary-purple text-white font-semibold hover:opacity-90 transition-all shadow-lg text-sm cursor-pointer disabled:opacity-50 mt-2"
          >
            {status === 'submitting' ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-gray-400">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary-cyan hover:underline font-medium">
            Create an Account
          </Link>
        </div>
      </div>
    </div>
  );
}
