/**
 * Match list component for displaying a list of upcoming matches.
 */

"use client";

import { useUpcomingMatches } from "@/hooks/use-predictions";
import { MatchCard } from "./match-card";

export function MatchList() {
  const { upcomingMatches, loading, error } = useUpcomingMatches();

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
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {upcomingMatches.map((match) => (
        <MatchCard key={match.fixtureId} match={match} />
      ))}
    </div>
  );
}
