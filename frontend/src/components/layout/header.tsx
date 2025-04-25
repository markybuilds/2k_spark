"use client";

/**
 * Header component for the application.
 */

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useRefresh } from '@/hooks/use-stats';

export function Header() {
  const { refreshData, loading, success, error } = useRefresh();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="flex items-center space-x-2">
            <span className="font-bold text-xl">2K Flash</span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <nav className="flex items-center space-x-4">
            <Link href="/" className="text-sm font-medium transition-colors hover:text-primary">
              Home
            </Link>
            <Link href="/predictions" className="text-sm font-medium transition-colors hover:text-primary">
              Predictions
            </Link>
            <Link href="/matches" className="text-sm font-medium transition-colors hover:text-primary">
              Matches
            </Link>
            <Link href="/players" className="text-sm font-medium transition-colors hover:text-primary">
              Players
            </Link>
            <Link href="/scores" className="text-sm font-medium transition-colors hover:text-primary">
              Scores
            </Link>
            <Link href="/history" className="text-sm font-medium transition-colors hover:text-primary">
              History
            </Link>
            <Link href="/stats" className="text-sm font-medium transition-colors hover:text-primary">
              Stats
            </Link>
          </nav>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => refreshData()}
              disabled={loading}
            >
              {loading ? 'Refreshing...' : 'Refresh Data'}
            </Button>
            {success && (
              <span className="text-xs text-green-500">Refresh successful!</span>
            )}
            {error && (
              <span className="text-xs text-red-500">Refresh failed</span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
