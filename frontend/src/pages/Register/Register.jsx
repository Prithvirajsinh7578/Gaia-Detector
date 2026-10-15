import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerUser } from '../../services/api';
import { HiOutlineUser, HiOutlineMail, HiOutlineLockClosed, HiOutlineCheckCircle, HiOutlineExclamationCircle } from 'react-icons/hi';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState(null); // 'submitting' | 'success' | 'error'
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password) {
      setStatus('error');
      setMessage('Please fill in all required fields.');
      return;
    }
    setStatus('submitting');
    try {
      await registerUser(name, email, password);
      setStatus('success');
      setMessage('Account registered successfully! Redirecting to login...');
      setTimeout(() => navigate('/login'), 1200);
    } catch (err) {
      setStatus('error');
      setMessage(err.message || 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen pt-32 pb-16 px-4 flex items-center justify-center">
      <div className="w-full max-w-md glass rounded-3xl p-8 border border-white/10 shadow-2xl">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-white mb-2 font-heading">
            Create an <span className="bg-gradient-to-r from-primary-cyan to-primary-purple bg-clip-text text-transparent">Account</span>
          </h2>
          <p className="text-gray-400 text-xs">
            Join Gaia Detector to track scan history and analyze multimedia files.
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
            <label className="text-gray-300 text-xs font-semibold block mb-1.5">Full Name</label>
            <div className="relative">
              <HiOutlineUser className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Doe"
                className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-white text-sm focus:outline-none focus:border-primary-cyan transition-colors"
              />
            </div>
          </div>

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
            {status === 'submitting' ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-gray-400">
          Already have an account?{' '}
          <Link to="/login" className="text-primary-cyan hover:underline font-medium">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
