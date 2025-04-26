"use client";

import React, { createContext, useContext, useState } from 'react';

interface RefreshContextType {
  refreshCounter: number;
  triggerRefresh: () => void;
}

const RefreshContext = createContext<RefreshContextType | undefined>(undefined);

export function RefreshProvider({ children }: { children: React.ReactNode }) {
  const [refreshCounter, setRefreshCounter] = useState(0);

  const triggerRefresh = () => {
    setRefreshCounter(prev => prev + 1);
  };

  return (
    <RefreshContext.Provider value={{ refreshCounter, triggerRefresh }}>
      {children}
    </RefreshContext.Provider>
  );
}

export function useRefreshContext() {
  const context = useContext(RefreshContext);
  if (context === undefined) {
    throw new Error('useRefreshContext must be used within a RefreshProvider');
  }
  return context;
}
