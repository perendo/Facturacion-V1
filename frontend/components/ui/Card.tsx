import React from "react";

interface CardProps {
  title?: string;
  className?: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
}

export default function Card({ title, className = "", children, actions }: CardProps) {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>
      {(title || actions) && (
        <div className="mb-4 flex items-center justify-between">
          {title && <h3 className="text-base font-semibold text-slate-800">{title}</h3>}
          {actions}
        </div>
      )}
      {children}
    </div>
  );
}