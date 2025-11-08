/**
 * Select Component
 * Dropdown select with label, error, and options
 */

import { ReactNode } from 'react';

interface SelectOption {
  value: string | number;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: SelectOption[];
  placeholder?: string;
  icon?: ReactNode;
  fullWidth?: boolean;
  containerClassName?: string;
}

export function Select({
  label,
  error,
  options,
  placeholder = 'Select an option',
  icon,
  fullWidth = true,
  containerClassName = '',
  className = '',
  ...props
}: SelectProps) {
  const baseClasses =
    'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all appearance-none';

  const errorClasses = error ? 'border-red-500 focus:ring-red-500' : '';

  const containerWidth = fullWidth ? 'w-full' : '';

  return (
    <div className={`${containerWidth} ${containerClassName}`}>
      {label && <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>}

      <div className="relative">
        {icon && <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">{icon}</div>}

        <select
          {...props}
          className={`${baseClasses} ${errorClasses} ${icon ? 'pl-10' : ''} pr-10 bg-white ${className}`}
        >
          <option value="">{placeholder}</option>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        {/* Chevron Icon */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </div>

      {error && <p className="text-sm text-red-600 mt-1">{error}</p>}
    </div>
  );
}
