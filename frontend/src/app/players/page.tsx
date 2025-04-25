/**
 * Players page for displaying player statistics.
 */

import { PlayerStatsList } from "@/components/players/player-stats-list";

export const metadata = {
  title: "Player Statistics - 2K Flash",
  description: "Player statistics for NBA 2K25 eSports players",
};

export default function PlayersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Player Statistics</h1>
        <p className="text-muted-foreground">
          View statistics for NBA 2K25 eSports players.
        </p>
      </div>
      
      <PlayerStatsList />
    </div>
  );
}
