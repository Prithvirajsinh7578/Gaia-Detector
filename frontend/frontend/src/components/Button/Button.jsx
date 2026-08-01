import { Link } from 'react-router-dom';

/**
 * Reusable button component with multiple variants.
 * Supports internal routing via React Router Link.
 */
export default function Button({
  children,
  variant = 'primary', // 'primary' | 'secondary' | 'outline' | 'ghost'
  size = 'md',         // 'sm' | 'md' | 'lg'
  to,                  // React Router path
  href,                // External link
  onClick,
  className = '',
  disabled = false,
  ...props
}) {
  const baseClasses = `
    btn-ripple inline-flex items-center justify-center gap-2
    font-semibold rounded-xl transition-all duration-300
    disabled:opacity-50 disabled:cursor-not-allowed
    cursor-pointer
  `;

  const variants = {
    primary: `
      bg-gradient-to-r from-primary-cyan to-primary-purple text-white
      hover:shadow-[0_0_30px_rgba(6,182,212,0.3)] hover:scale-[1.02]
      active:scale-[0.98]
    `,
    secondary: `
      bg-white/10 text-white border border-white/20
      hover:bg-white/15 hover:border-white/30
      hover:shadow-[0_0_20px_rgba(255,255,255,0.05)]
      active:scale-[0.98]
    `,
    outline: `
      bg-transparent text-primary-cyan border border-primary-cyan/50
      hover:bg-primary-cyan/10 hover:border-primary-cyan
      hover:shadow-[0_0_20px_rgba(6,182,212,0.15)]
      active:scale-[0.98]
    `,
    ghost: `
      bg-transparent text-gray-300
      hover:text-white hover:bg-white/5
      active:scale-[0.98]
    `,
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  const classes = `${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`;

  if (to) {
    return (
      <Link to={to} className={classes} {...props}>
        {children}
      </Link>
    );
  }

  if (href) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer" className={classes} {...props}>
        {children}
      </a>
    );
  }

  return (
    <button onClick={onClick} disabled={disabled} className={classes} {...props}>
      {children}
    </button>
  );
}
