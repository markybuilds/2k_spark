/**
 * Prediction list component for displaying a list of match predictions.
 */

"use client";

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { PredictionCard } from "./prediction-card";

export function PredictionList() {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        setLoading(true);
        console.log('PredictionList: Fetching predictions directly...');

        // Make the API request with fetch directly
        const response = await fetch(`http://localhost:5000/api/predictions?timestamp=${Date.now()}`);

        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }

        const data = await response.json();
        console.log(`PredictionList: Fetched predictions directly, response:`, data);

        let predictionsData = [];

        if (Array.isArray(data)) {
          console.log(`PredictionList: Fetched ${data.length} predictions directly (array format)`);
          predictionsData = data;
        } else if (data && typeof data === 'object' && Array.isArray(data.predictions)) {
          console.log(`PredictionList: Fetched ${data.predictions.length} predictions directly (object format)`);
          predictionsData = data.predictions;
        } else {
          console.error('PredictionList: Unexpected API response format:', data);
          setError('Unexpected API response format');
          setPredictions([]);
          return;
        }

        // Filter out matches that have already started
        const now = new Date();
        console.log('Current time:', now.toISOString());

        const upcomingMatches = predictionsData.filter(match => {
          // Parse the fixture start time
          const fixtureStart = new Date(match.fixtureStart);

          // Only include matches that haven't started yet
          const isUpcoming = fixtureStart > now;
          console.log(`Match ${match.fixtureId} start time: ${fixtureStart.toISOString()}, is upcoming: ${isUpcoming}`);

          return isUpcoming;
        });

        console.log(`Showing ${upcomingMatches.length} upcoming matches after filtering out ${predictionsData.length - upcomingMatches.length} matches that have already started`);

        // Sort by start time (earliest first)
        upcomingMatches.sort((a, b) => {
          return new Date(a.fixtureStart).getTime() - new Date(b.fixtureStart).getTime();
        });

        setPredictions(upcomingMatches);

        setError(null);
      } catch (err) {
        console.error('PredictionList: Error fetching predictions:', err);
        setError(`Failed to fetch predictions: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
  }, []);

  // Debug information
  console.log('PredictionList - predictions:', predictions);

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
