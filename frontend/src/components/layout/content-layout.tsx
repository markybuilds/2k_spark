"use client";

import React from "react";
import { cn } from "@/lib/utils";

interface ContentLayoutProps {
  children: React.ReactNode;
  className?: string;
  fullWidth?: boolean;
}

export function ContentLayout({
  children,
  className,
  fullWidth = false,
}: ContentLayoutProps) {
  return (
    <div className={cn(
      "space-y-8",
      !fullWidth && "content-layout",
      className
    )}>
      {children}
    </div>
  );
}

export function PageHeader({
  title,
  description,
  className,
}: {
  title: string;
  description?: string;
  className?: string;
}) {
  return (
    <div className={cn("mb-10", className)}>
      <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
      {description && (
        <p className="mt-3 text-muted-foreground text-lg">{description}</p>
      )}
    </div>
  );
}
