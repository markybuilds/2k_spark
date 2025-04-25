"use client";

/**
 * Header component for the application.
 */

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useRefresh } from '@/hooks/use-stats';
import { ThemeToggle } from '@/components/theme';
import { RefreshCw } from 'lucide-react';

export function Header() {
  const { refreshData, loading, success, error } = useRefresh();
  const pathname = usePathname();

  const isActive = (path: string) => {
    if (path === '/' && pathname !== '/') return false;
    return pathname === path || pathname.startsWith(`${path}/`);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container-centered flex h-16 items-center">
        <div className="mr-6 flex">
          <Link href="/" className="flex items-center space-x-2">
            <div className="flex items-center justify-center w-8 h-8 rounded-md bg-primary text-primary-foreground">
              <span className="font-bold text-sm">2K</span>
            </div>
            <span className="font-bold text-xl gradient-text">2K Flash</span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <nav className="flex items-center space-x-1">
            <Link href="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>
              Home
            </Link>
            <Link href="/predictions" className={`nav-link ${isActive('/predictions') ? 'active' : ''}`}>
              Predictions
            </Link>
            <Link href="/matches" className={`nav-link ${isActive('/matches') ? 'active' : ''}`}>
              Matches
            </Link>
            <Link href="/players" className={`nav-link ${isActive('/players') ? 'active' : ''}`}>
              Players
            </Link>
            <Link href="/scores" className={`nav-link ${isActive('/scores') ? 'active' : ''}`}>
              Scores
            </Link>
            <Link href="/history" className={`nav-link ${isActive('/history') ? 'active' : ''}`}>
              History
            </Link>
            <Link href="/stats" className={`nav-link ${isActive('/stats') ? 'active' : ''}`}>
              Stats
            </Link>
          </nav>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refreshData()}
              disabled={loading}
              className="flex items-center gap-1"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Refreshing...' : 'Refresh'}
            </Button>
            {success && (
              <span className="text-xs text-green-500">Refresh successful!</span>
            )}
            {error && (
              <span className="text-xs text-red-500">Refresh failed</span>
            )}
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  );
}
