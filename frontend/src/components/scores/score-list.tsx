/**
 * Score list component for displaying a list of score predictions.
 */

"use client";

import { useScorePredictions } from "@/hooks/use-predictions";
import { ScoreCard } from "./score-card";

export function ScoreList() {
  const { predictions, modelAccuracy, loading, error } = useScorePredictions();

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading score predictions...</p>
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

  if (!predictions || predictions.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <p className="text-muted-foreground">No upcoming score predictions available.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-6 p-4 bg-muted rounded-lg">
        <p className="text-sm text-muted-foreground">
          <strong>Model Accuracy:</strong> The score prediction model has an average error of {modelAccuracy.toFixed(1)} points.
        </p>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {predictions.map((prediction) => (
          <ScoreCard key={prediction.fixtureId} prediction={prediction} />
        ))}
      </div>
    </div>
  );
}
