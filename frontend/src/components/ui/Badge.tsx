/**
 * Badge Component
 * Inline label for status, tags, etc.
 */

interface BadgeProps {
  children: string | number;
  variant?: 'default' | 'success' | 'danger' | 'warning' | 'info';
  size?: 'sm' | 'md';
  className?: string;
}

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}: BadgeProps) {
  const variantClasses = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    danger: 'bg-red-100 text-red-800',
    warning: 'bg-yellow-100 text-yellow-800',
    info: 'bg-blue-100 text-blue-800',
  };

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  };

  return (
    <span
      className={`inline-block rounded-full font-medium ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {children}
    </span>
  );
}
