/**
 * Card Component
 * Container for content with optional header and footer
 */

import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  header?: ReactNode;
  footer?: ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
  onClick?: () => void;
  hover?: boolean;
}

export function Card({
  children,
  header,
  footer,
  title,
  subtitle,
  className = '',
  onClick,
  hover = false,
}: CardProps) {
  const hoverClass = hover ? 'hover:shadow-lg cursor-pointer' : '';

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-lg border border-gray-200 shadow transition-shadow duration-200 ${hoverClass} ${className}`}
    >
      {/* Header */}
      {(header || title) && (
        <div className="px-6 py-4 border-b border-gray-200">
          {header ? (
            header
          ) : (
            <div>
              {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
              {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
            </div>
          )}
        </div>
      )}

      {/* Body */}
      <div className="px-6 py-4">{children}</div>

      {/* Footer */}
      {footer && <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">{footer}</div>}
    </div>
  );
}
