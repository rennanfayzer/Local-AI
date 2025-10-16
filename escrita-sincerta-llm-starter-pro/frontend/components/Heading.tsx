import React from 'react';

interface HeadingProps {
  children: React.ReactNode;
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
  className?: string;
}

const Heading: React.FC<HeadingProps> = ({ children, as: Tag = 'h2', className = '' }) => {
  const baseClasses = 'font-bold tracking-tight';
  const sizeClasses = {
    h1: 'text-4xl',
    h2: 'text-2xl border-b pb-2',
    h3: 'text-xl',
    h4: 'text-lg',
    h5: 'text-base',
    h6: 'text-sm',
  };

  return (
    <Tag className={`${baseClasses} ${sizeClasses[Tag]} ${className}`}>
      {children}
    </Tag>
  );
};

export default Heading;