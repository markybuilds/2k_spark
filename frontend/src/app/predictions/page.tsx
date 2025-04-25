/**
 * Predictions page for displaying match predictions.
 */

import { PredictionList } from "@/components/predictions/prediction-list";

export const metadata = {
  title: "Match Predictions - 2K Flash",
  description: "Predictions for upcoming NBA 2K25 eSports matches",
};

export default function PredictionsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Match Predictions</h1>
        <p className="text-muted-foreground">
          View predictions for upcoming NBA 2K25 eSports matches.
        </p>
      </div>
      
      <PredictionList />
    </div>
  );
}
