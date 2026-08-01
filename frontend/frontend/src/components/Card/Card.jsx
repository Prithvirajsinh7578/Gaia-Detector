import { motion } from 'framer-motion';

/**
 * Glassmorphism card component with optional hover glow effect.
 */
export default function GlassCard({
  children,
  className = '',
  hover = true,
  glowColor = 'cyan', // 'cyan' | 'purple'
  ...props
}) {
  const glowMap = {
    cyan: 'hover:shadow-[0_0_30px_rgba(6,182,212,0.15)]',
    purple: 'hover:shadow-[0_0_30px_rgba(168,85,247,0.15)]',
  };

  return (
    <motion.div
      className={`
        glass rounded-2xl p-6
        ${hover ? `transition-all duration-300 hover:bg-white/[0.08] ${glowMap[glowColor]}` : ''}
        ${className}
      `}
      whileHover={hover ? { scale: 1.02, y: -4 } : {}}
      transition={{ duration: 0.3 }}
      {...props}
    >
      {children}
    </motion.div>
  );
}
