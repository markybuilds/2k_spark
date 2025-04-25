/**
 * Stats page for displaying prediction statistics.
 */

import { StatsCards } from "@/components/stats/stats-cards";

export const metadata = {
  title: "Statistics - 2K Flash",
  description: "Prediction statistics and metrics for NBA 2K25 eSports matches",
};

export default function StatsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Statistics</h1>
        <p className="text-muted-foreground">
          View prediction statistics and metrics for NBA 2K25 eSports matches.
        </p>
      </div>
      
      <StatsCards />
    </div>
  );
}
