/**
 * Section wrapper with consistent heading styling.
 */
export default function SectionHeading({
  title,
  subtitle,
  centered = true,
  className = '',
}) {
  return (
    <div className={`mb-16 ${centered ? 'text-center' : ''} ${className}`}>
      <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
        <span className="gradient-text">{title}</span>
      </h2>
      {subtitle && (
        <p className="text-gray-400 text-lg max-w-2xl mx-auto leading-relaxed">
          {subtitle}
        </p>
      )}
    </div>
  );
}
