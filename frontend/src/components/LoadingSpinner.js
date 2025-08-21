import React from 'react';
import { clsx } from 'clsx';

const LoadingSpinner = ({ 
  size = 'medium', 
  color = 'primary', 
  className,
  message 
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-6 h-6',
    large: 'w-8 h-8',
    xl: 'w-12 h-12',
  };

  const colorClasses = {
    primary: 'border-primary-600',
    secondary: 'border-secondary-600',
    white: 'border-white',
    success: 'border-success-600',
    warning: 'border-warning-600',
    error: 'border-error-600',
  };

  return (
    <div className={clsx(
      'flex flex-col items-center justify-center space-y-2',
      className
    )}>
      <div
        className={clsx(
          'animate-spin rounded-full border-2 border-t-transparent',
          sizeClasses[size],
          colorClasses[color]
        )}
      />
      {message && (
        <p className="text-sm text-secondary-600 animate-pulse">
          {message}
        </p>
      )}
    </div>
  );
};

export default LoadingSpinner;
