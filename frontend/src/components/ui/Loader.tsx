/**
 * Loader Component
 * Loading skeleton and spinners
 */

interface SkeletonProps {
  count?: number;
  height?: number;
  width?: string;
  circle?: boolean;
  className?: string;
}

export function Skeleton({
  count = 1,
  height = 20,
  width = 'w-full',
  circle = false,
  className = '',
}: SkeletonProps) {
  const circleClass = circle ? 'rounded-full' : 'rounded';

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={`bg-gray-200 animate-pulse ${circleClass} ${width} ${className}`}
          style={{ height: `${height}px` }}
        />
      ))}
    </>
  );
}

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
}

export function LoadingSpinner({ size = 'md', message = 'Loading...' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className={`${sizeClasses[size]} animate-spin`}>
        <svg
          className="w-full h-full text-blue-600"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      </div>
      <p className={`text-gray-600 ${textSizeClasses[size]}`}>{message}</p>
    </div>
  );
}

interface ProgressBarProps {
  progress: number; // 0-100
  showLabel?: boolean;
  color?: 'blue' | 'green' | 'red' | 'yellow';
}

export function ProgressBar({
  progress,
  showLabel = true,
  color = 'blue',
}: ProgressBarProps) {
  const colorClasses = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    red: 'bg-red-600',
    yellow: 'bg-yellow-600',
  };

  return (
    <div className="w-full">
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]} transition-all duration-300`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-gray-600 mt-1">{Math.round(progress)}%</p>
      )}
    </div>
  );
}
