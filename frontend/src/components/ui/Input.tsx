/**
 * Input Component
 * Text input with label, error, and variants
 */

import { ReactNode } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  icon?: ReactNode;
  fullWidth?: boolean;
  containerClassName?: string;
}

export function Input({
  label,
  error,
  hint,
  icon,
  fullWidth = true,
  containerClassName = '',
  className = '',
  ...props
}: InputProps) {
  const baseClasses =
    'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all';

  const errorClasses = error ? 'border-red-500 focus:ring-red-500' : '';

  const containerWidth = fullWidth ? 'w-full' : '';

  return (
    <div className={`${containerWidth} ${containerClassName}`}>
      {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>}

      <div className="relative">
        {icon && <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">{icon}</div>}
        <input
          {...props}
          className={`${baseClasses} ${errorClasses} ${icon ? 'pl-10' : ''} ${className}`}
        />
      </div>

      {error && <p className="text-sm text-red-600 mt-1">{error}</p>}
      {hint && !error && <p className="text-sm text-gray-500 mt-1">{hint}</p>}
    </div>
  );
}
