import { Link } from 'react-router-dom';
import { FaGithub, FaLinkedin, FaTwitter } from 'react-icons/fa';
import { FOOTER_LINKS } from '../../constants/constants';

export default function Footer() {
  return (
    <footer className="relative border-t border-white/5">
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-dark-base via-dark-navy/50 to-transparent pointer-events-none" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="lg:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary-cyan to-primary-purple flex items-center justify-center">
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
            <p className="text-gray-500 text-sm leading-relaxed mb-6">
              Advanced AI-powered content authenticity detection. Verify text, images, videos, and documents with confidence.
            </p>
            <div className="flex items-center gap-3">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-xl glass flex items-center justify-center text-gray-400 hover:text-primary-cyan hover:bg-primary-cyan/10 transition-all duration-300">
                <FaGithub size={18} />
              </a>
              <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-xl glass flex items-center justify-center text-gray-400 hover:text-primary-cyan hover:bg-primary-cyan/10 transition-all duration-300">
                <FaLinkedin size={18} />
              </a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-xl glass flex items-center justify-center text-gray-400 hover:text-primary-cyan hover:bg-primary-cyan/10 transition-all duration-300">
                <FaTwitter size={18} />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-white font-semibold font-heading mb-4">Quick Links</h3>
            <ul className="space-y-3">
              {FOOTER_LINKS.quickLinks.map((link) => (
                <li key={link.name}>
                  <Link to={link.path} className="text-gray-500 hover:text-primary-cyan transition-colors duration-300 text-sm">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-white font-semibold font-heading mb-4">Resources</h3>
            <ul className="space-y-3">
              {FOOTER_LINKS.resources.map((link) => (
                <li key={link.name}>
                  <Link to={link.path} className="text-gray-500 hover:text-primary-cyan transition-colors duration-300 text-sm">
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-white font-semibold font-heading mb-4">Contact</h3>
            <ul className="space-y-3">
              {FOOTER_LINKS.contact.map((link) => (
                <li key={link.name}>
                  <a href={link.path} target={link.path.startsWith('http') ? '_blank' : undefined} rel="noopener noreferrer" className="text-gray-500 hover:text-primary-cyan transition-colors duration-300 text-sm">
                    {link.name}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-gray-600 text-sm">
            Â© {new Date().getFullYear()} Gaia Detector. All rights reserved.
          </p>
          <div className="flex items-center gap-6">
            <Link to="#" className="text-gray-600 hover:text-gray-400 text-sm transition-colors">Privacy Policy</Link>
            <Link to="#" className="text-gray-600 hover:text-gray-400 text-sm transition-colors">Terms of Service</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
