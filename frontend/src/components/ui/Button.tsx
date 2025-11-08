/**
 * Button Component
 * Reusable button with variants and states
 */

import { ReactNode } from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  isLoading?: boolean;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  isLoading = false,
  leftIcon,
  rightIcon,
  disabled,
  className = '',
  ...props
}: ButtonProps) {
  const baseClasses =
    'font-medium rounded-lg transition-colors duration-200 flex items-center justify-center gap-2';

  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 disabled:bg-gray-400 text-gray-900',
    danger: 'bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white',
    success: 'bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white',
    warning: 'bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-400 text-white',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };

  const widthClass = fullWidth ? 'w-full' : '';

  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${widthClass} ${className}`}
    >
      {isLoading && <span className="animate-spin">⏳</span>}
      {!isLoading && leftIcon && <span>{leftIcon}</span>}
      <span>{children}</span>
      {!isLoading && rightIcon && <span>{rightIcon}</span>}
    </button>
  );
}
