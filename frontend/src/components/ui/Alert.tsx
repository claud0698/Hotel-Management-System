/**
 * Alert Component
 * Display alerts/notifications inline
 */

import { ReactNode } from 'react';

interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title?: string;
  message: string | ReactNode;
  onClose?: () => void;
  dismissible?: boolean;
}

export function Alert({
  type,
  title,
  message,
  onClose,
  dismissible = true,
}: AlertProps) {
  const typeConfig = {
    success: {
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-700',
      titleColor: 'text-green-800',
      icon: '✓',
      iconBg: 'bg-green-100 text-green-700',
    },
    error: {
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-700',
      titleColor: 'text-red-800',
      icon: '✕',
      iconBg: 'bg-red-100 text-red-700',
    },
    warning: {
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-700',
      titleColor: 'text-yellow-800',
      icon: '⚠',
      iconBg: 'bg-yellow-100 text-yellow-700',
    },
    info: {
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-700',
      titleColor: 'text-blue-800',
      icon: 'ℹ',
      iconBg: 'bg-blue-100 text-blue-700',
    },
  };

  const config = typeConfig[type];

  return (
    <div className={`${config.bgColor} border ${config.borderColor} rounded-lg p-4 flex gap-3`}>
      <div className={`${config.iconBg} rounded-full w-6 h-6 flex items-center justify-center flex-shrink-0 font-bold text-sm`}>
        {config.icon}
      </div>

      <div className="flex-1 min-w-0">
        {title && <h4 className={`${config.titleColor} font-semibold text-sm mb-1`}>{title}</h4>}
        <p className={`${config.textColor} text-sm`}>{message}</p>
      </div>

      {dismissible && onClose && (
        <button
          onClick={onClose}
          className={`${config.textColor} hover:opacity-75 flex-shrink-0 font-bold text-lg transition-opacity`}
        >
          ×
        </button>
      )}
    </div>
  );
}
