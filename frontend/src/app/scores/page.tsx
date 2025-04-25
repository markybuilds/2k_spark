/**
 * Scores page for displaying score predictions.
 */

import { ScoreList } from "@/components/scores/score-list";

export const metadata = {
  title: "Score Predictions - 2K Flash",
  description: "Score predictions for upcoming NBA 2K25 eSports matches",
};

export default function ScoresPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Score Predictions</h1>
        <p className="text-muted-foreground">
          View score predictions for upcoming NBA 2K25 eSports matches.
        </p>
      </div>
      
      <ScoreList />
    </div>
  );
}
