/**
 * Prediction list component for displaying a list of match predictions.
 */

"use client";

import { usePredictions } from "@/hooks/use-predictions";
import { PredictionCard } from "./prediction-card";

export function PredictionList() {
  const { predictions, loading, error } = usePredictions();

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading predictions...</p>
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
          <p className="text-muted-foreground">No upcoming match predictions available.</p>
          <p className="mt-2 text-sm text-muted-foreground">
            All scheduled matches have already started or there are no matches scheduled.
          </p>
          <p className="mt-2 text-sm text-muted-foreground">
            Check back later for new upcoming matches or use the refresh button to update the data.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
      {predictions.map((prediction) => (
        <PredictionCard key={prediction.fixtureId} prediction={prediction} />
      ))}
    </div>
  );
}
