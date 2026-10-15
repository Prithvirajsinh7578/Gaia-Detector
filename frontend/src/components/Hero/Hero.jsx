import { motion } from 'framer-motion';
import { fadeLeft, fadeRight, staggerContainer, fadeUp } from '../../utils/animations';
import { HERO_BADGES } from '../../constants/constants';
import Button from '../Button/Button';
import Badge from '../Badge/Badge';

function HeroIllustration() {
  return (
    <div className="relative w-full h-[400px] md:h-[500px]">
      {/* Central AI Chip */}
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-24 h-24 md:w-32 md:h-32"
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      >
        <div className="w-full h-full rounded-2xl bg-gradient-to-br from-primary-cyan/20 to-primary-purple/20 border border-primary-cyan/30 flex items-center justify-center glow-cyan">
          <svg width="40" height="40" viewBox="0 0 40 40" className="text-primary-cyan">
            <rect x="8" y="8" width="24" height="24" rx="4" stroke="currentColor" strokeWidth="1.5" fill="none"/>
            <rect x="14" y="14" width="12" height="12" rx="2" fill="currentColor" opacity="0.3"/>
            <line x1="20" y1="0" x2="20" y2="8" stroke="currentColor" strokeWidth="1.5"/>
            <line x1="20" y1="32" x2="20" y2="40" stroke="currentColor" strokeWidth="1.5"/>
            <line x1="0" y1="20" x2="8" y2="20" stroke="currentColor" strokeWidth="1.5"/>
            <line x1="32" y1="20" x2="40" y2="20" stroke="currentColor" strokeWidth="1.5"/>
            <line x1="12" y1="0" x2="12" y2="8" stroke="currentColor" strokeWidth="1" opacity="0.5"/>
            <line x1="28" y1="0" x2="28" y2="8" stroke="currentColor" strokeWidth="1" opacity="0.5"/>
            <line x1="12" y1="32" x2="12" y2="40" stroke="currentColor" strokeWidth="1" opacity="0.5"/>
            <line x1="28" y1="32" x2="28" y2="40" stroke="currentColor" strokeWidth="1" opacity="0.5"/>
          </svg>
        </div>
      </motion.div>

      {/* Neural Network Lines */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 500">
        <motion.line x1="200" y1="250" x2="80" y2="100" stroke="url(#grad1)" strokeWidth="1" opacity="0.3"
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 2, delay: 0.5 }}/>
        <motion.line x1="200" y1="250" x2="320" y2="80" stroke="url(#grad1)" strokeWidth="1" opacity="0.3"
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 2, delay: 0.7 }}/>
        <motion.line x1="200" y1="250" x2="340" y2="350" stroke="url(#grad1)" strokeWidth="1" opacity="0.3"
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 2, delay: 0.9 }}/>
        <motion.line x1="200" y1="250" x2="60" y2="380" stroke="url(#grad1)" strokeWidth="1" opacity="0.3"
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 2, delay: 1.1 }}/>
        <motion.line x1="200" y1="250" x2="160" y2="420" stroke="url(#grad1)" strokeWidth="1" opacity="0.3"
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 2, delay: 1.3 }}/>
        <defs>
          <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.5"/>
            <stop offset="100%" stopColor="#a855f7" stopOpacity="0.5"/>
          </linearGradient>
        </defs>
      </svg>

      {/* Floating Document Icon */}
      <motion.div
        className="absolute top-[15%] left-[10%]"
        animate={{ y: [0, -15, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
      >
        <div className="w-14 h-14 md:w-16 md:h-16 rounded-xl glass flex items-center justify-center glow-purple">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-primary-purple">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M14 2v6h6" stroke="currentColor" strokeWidth="1.5"/>
            <line x1="8" y1="13" x2="16" y2="13" stroke="currentColor" strokeWidth="1.5" opacity="0.5"/>
            <line x1="8" y1="17" x2="12" y2="17" stroke="currentColor" strokeWidth="1.5" opacity="0.5"/>
          </svg>
        </div>
      </motion.div>

      {/* Floating Image Icon */}
      <motion.div
        className="absolute top-[10%] right-[15%]"
        animate={{ y: [0, -20, 0] }}
        transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
      >
        <div className="w-14 h-14 md:w-16 md:h-16 rounded-xl glass flex items-center justify-center glow-cyan">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-primary-cyan">
            <rect x="3" y="3" width="18" height="18" rx="3" stroke="currentColor" strokeWidth="1.5"/>
            <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" opacity="0.5"/>
            <path d="M21 15l-5-5L5 21" stroke="currentColor" strokeWidth="1.5"/>
          </svg>
        </div>
      </motion.div>

      {/* Floating Video Icon */}
      <motion.div
        className="absolute bottom-[20%] right-[10%]"
        animate={{ y: [0, -12, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
      >
        <div className="w-14 h-14 md:w-16 md:h-16 rounded-xl glass flex items-center justify-center glow-purple">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-primary-purple">
            <rect x="2" y="4" width="15" height="16" rx="2" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M17 8l5-3v14l-5-3V8z" stroke="currentColor" strokeWidth="1.5" fill="currentColor" opacity="0.2"/>
          </svg>
        </div>
      </motion.div>

      {/* Floating Shield Icon */}
      <motion.div
        className="absolute bottom-[25%] left-[5%]"
        animate={{ y: [0, -18, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
      >
        <div className="w-12 h-12 md:w-14 md:h-14 rounded-xl glass flex items-center justify-center">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" className="text-emerald-400">
            <path d="M12 2l8 4v6c0 5.5-3.5 10-8 11-4.5-1-8-5.5-8-11V6l8-4z" stroke="currentColor" strokeWidth="1.5" fill="currentColor" opacity="0.1"/>
            <path d="M9 12l2 2 4-4" stroke="currentColor" strokeWidth="2"/>
          </svg>
        </div>
      </motion.div>

      {/* Additional small floating dots */}
      <motion.div className="absolute top-[40%] right-[30%] w-2 h-2 rounded-full bg-primary-cyan/50"
        animate={{ y: [0, -8, 0], opacity: [0.3, 0.8, 0.3] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div className="absolute top-[60%] left-[25%] w-3 h-3 rounded-full bg-primary-purple/50"
        animate={{ y: [0, -10, 0], opacity: [0.3, 0.7, 0.3] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 1.5 }}
      />
      <motion.div className="absolute top-[30%] left-[40%] w-1.5 h-1.5 rounded-full bg-primary-cyan/40"
        animate={{ y: [0, -6, 0], opacity: [0.2, 0.6, 0.2] }}
        transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut', delay: 0.8 }}
      />
    </div>
  );
}

export default function Hero() {
  return (
    <section className="min-h-screen flex items-center pt-20 section-padding relative overflow-hidden">
      <div className="max-w-7xl mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left Side - Content */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
          >
            <motion.div variants={fadeLeft} className="mb-4">
              <Badge variant="cyan" size="sm" icon="ðŸ”¬">
                AI-Powered Detection Engine
              </Badge>
            </motion.div>

            <motion.h1
              variants={fadeLeft}
              className="text-4xl md:text-5xl lg:text-6xl font-bold font-heading leading-tight mb-6"
            >
              Detect AI Generated Content with{' '}
              <span className="gradient-text">Confidence</span>
            </motion.h1>

            <motion.p
              variants={fadeLeft}
              className="text-gray-400 text-lg md:text-xl leading-relaxed mb-8 max-w-xl"
            >
              Analyze text, images, videos, and documents using advanced AI-powered
              authenticity detection. Stay ahead in the age of synthetic content.
            </motion.p>

            <motion.div variants={fadeLeft} className="flex flex-wrap gap-4 mb-10">
              <Button variant="primary" size="lg" to="#upload-demo">
                Try Demo
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M5 12h14M12 5l7 7-7 7"/>
                </svg>
              </Button>
              <Button variant="secondary" size="lg" to="/features">
                Learn More
              </Button>
            </motion.div>

            <motion.div variants={fadeUp} className="flex flex-wrap gap-3">
              {HERO_BADGES.map((badge) => (
                <Badge key={badge.label} variant="default" icon={badge.icon}>
                  {badge.label}
                </Badge>
              ))}
            </motion.div>
          </motion.div>

          {/* Right Side - Illustration */}
          <motion.div
            variants={fadeRight}
            initial="hidden"
            animate="visible"
            className="hidden lg:block"
          >
            <HeroIllustration />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
