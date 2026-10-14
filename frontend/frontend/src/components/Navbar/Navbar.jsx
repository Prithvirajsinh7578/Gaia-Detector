import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { HiMenuAlt3, HiX } from 'react-icons/hi';
import { useScrollPosition } from '../../hooks/useScrollPosition';
import { NAV_LINKS } from '../../constants/constants';
import Button from '../Button/Button';
import { useAuth } from '../../context/AuthContext';
import { ROUTES } from '../../constants/routes';

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { isScrolled } = useScrollPosition();
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const isActive = (path) => location.pathname === path;

  const handleLogout = async () => {
    await logout();
    navigate(ROUTES.HOME);
  };

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={`
        fixed top-0 left-0 right-0 z-50 transition-all duration-500
        ${isScrolled
          ? 'bg-dark-base/80 backdrop-blur-xl border-b border-white/5 shadow-lg shadow-black/20'
          : 'bg-transparent'
        }
      `}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-cyan to-primary-purple flex items-center justify-center transition-transform duration-300 group-hover:scale-110">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="text-white">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="text-xl font-bold font-heading">
              <span className="text-white">Gaia</span>
              <span className="gradient-text"> Detector</span>
            </span>
          </Link>

          {/* Desktop Nav Links */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`
                  px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300
                  ${isActive(link.path)
                    ? 'text-primary-cyan bg-primary-cyan/10'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }
                `}
              >
                {link.name}
              </Link>
            ))}
            {user && (
              <>
                <Link
                  to={ROUTES.DASHBOARD}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300
                    ${isActive(ROUTES.DASHBOARD)
                      ? 'text-primary-cyan bg-primary-cyan/10'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }
                  `}
                >
                  Dashboard
                </Link>
                <Link
                  to={ROUTES.UPLOAD}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300
                    ${isActive(ROUTES.UPLOAD)
                      ? 'text-primary-cyan bg-primary-cyan/10'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }
                  `}
                >
                  Detect
                </Link>
                <Link
                  to={ROUTES.HISTORY}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300
                    ${isActive(ROUTES.HISTORY)
                      ? 'text-primary-cyan bg-primary-cyan/10'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }
                  `}
                >
                  History
                </Link>
              </>
            )}
          </div>

          {/* Desktop Auth Buttons */}
          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-400">
                  Hi, <span className="text-white font-medium">{user.name || user.email}</span>
                </span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors cursor-pointer"
                >
                  Logout
                </button>
              </div>
            ) : (
              <>
                <Button variant="ghost" size="sm" to={ROUTES.LOGIN}>Login</Button>
                <Button variant="primary" size="sm" to={ROUTES.REGISTER}>Register</Button>
              </>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
            aria-label="Toggle menu"
          >
            {mobileOpen ? <HiX size={24} /> : <HiMenuAlt3 size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden glass-strong border-t border-white/5 overflow-hidden"
          >
            <div className="px-4 py-4 space-y-1">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setMobileOpen(false)}
                  className={`
                    block px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300
                    ${isActive(link.path)
                      ? 'text-primary-cyan bg-primary-cyan/10'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }
                  `}
                >
                  {link.name}
                </Link>
              ))}
              {user ? (
                <div className="pt-2 border-t border-white/10 mt-2 space-y-1">
                  <Link
                    to={ROUTES.DASHBOARD}
                    onClick={() => setMobileOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-300 hover:text-white"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to={ROUTES.UPLOAD}
                    onClick={() => setMobileOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-300 hover:text-white"
                  >
                    Detect
                  </Link>
                  <Link
                    to={ROUTES.HISTORY}
                    onClick={() => setMobileOpen(false)}
                    className="block px-4 py-2 text-sm text-gray-300 hover:text-white"
                  >
                    History
                  </Link>
                  <button
                    onClick={() => { setMobileOpen(false); handleLogout(); }}
                    className="w-full text-left px-4 py-2 text-sm text-red-400 hover:text-red-300"
                  >
                    Logout ({user.name || user.email})
                  </button>
                </div>
              ) : (
                <div className="flex gap-3 pt-4 border-t border-white/10 mt-2">
                  <Button variant="secondary" size="sm" to={ROUTES.LOGIN} className="flex-1" onClick={() => setMobileOpen(false)}>
                    Login
                  </Button>
                  <Button variant="primary" size="sm" to={ROUTES.REGISTER} className="flex-1" onClick={() => setMobileOpen(false)}>
                    Register
                  </Button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
}
