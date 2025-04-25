/**
 * Matches page for displaying upcoming matches.
 */

import { MatchList } from "@/components/matches/match-list";

export const metadata = {
  title: "Upcoming Matches - 2K Flash",
  description: "Upcoming NBA 2K25 eSports matches",
};

export default function MatchesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Upcoming Matches</h1>
        <p className="text-muted-foreground">
          View upcoming NBA 2K25 eSports matches.
        </p>
      </div>
      
      <MatchList />
    </div>
  );
}
