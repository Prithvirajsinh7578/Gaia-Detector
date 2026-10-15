/**
 * Small badge/chip component for labels and tags.
 */
export default function Badge({
  children,
  variant = 'default', // 'default' | 'cyan' | 'purple' | 'success' | 'warning' | 'danger'
  size = 'md',
  icon,
  className = '',
}) {
  const variants = {
    default: 'bg-white/10 text-gray-300 border-white/10',
    cyan: 'bg-primary-cyan/10 text-primary-cyan border-primary-cyan/20',
    purple: 'bg-primary-purple/10 text-primary-purple border-primary-purple/20',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    danger: 'bg-red-500/10 text-red-400 border-red-500/20',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full border font-medium
        transition-all duration-300 hover:scale-105
        ${variants[variant]} ${sizes[size]} ${className}
      `}
    >
      {icon && <span>{icon}</span>}
      {children}
    </span>
  );
}
