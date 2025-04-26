/**
 * Match list component for displaying a list of upcoming matches.
 */

"use client";

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { MatchCard } from "./match-card";

export function MatchList() {
  const [upcomingMatches, setUpcomingMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUpcomingMatches = async () => {
      try {
        setLoading(true);

        const data = await apiClient.getUpcomingMatches();

        // Filter out matches that have already started
        const now = new Date();

        const filteredMatches = data.filter(match => {
          // Parse the fixture start time
          const fixtureStart = new Date(match.fixtureStart);

          // Only include matches that haven't started yet
          const isUpcoming = fixtureStart > now;

          return isUpcoming;
        });

        // Sort by start time (earliest first)
        filteredMatches.sort((a, b) => {
          return new Date(a.fixtureStart).getTime() - new Date(b.fixtureStart).getTime();
        });

        setUpcomingMatches(filteredMatches);
        setError(null);
      } catch (err) {
        setError('Failed to fetch upcoming matches. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchUpcomingMatches();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading upcoming matches...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <p className="text-red-500">{error}</p>
          <p className="mt-2 text-muted-foreground">Please try again later.</p>
        </div>
      </div>
    );
  }

  if (!upcomingMatches || upcomingMatches.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <p className="text-muted-foreground">No upcoming matches available.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
      {upcomingMatches.map((match) => (
        <MatchCard key={match.id || `${match.homePlayer?.id}-${match.awayPlayer?.id}-${match.fixtureStart}`} match={match} />
      ))}
    </div>
  );
}
