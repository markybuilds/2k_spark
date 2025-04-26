/**
 * Live match list component for displaying a list of live matches.
 */

"use client";

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';
import { LiveMatchCard } from "./live-match-card";

export function LiveMatchList() {
  const [liveMatches, setLiveMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLiveMatches = async () => {
      try {
        setLoading(true);

        // Fetch both predictions and upcoming matches
        const [predictionsData, upcomingMatchesData, scorePredictionsData] = await Promise.all([
          apiClient.getPredictions(),
          apiClient.getUpcomingMatches(),
          apiClient.getScorePredictions()
        ]);

        // Create a map of fixture IDs to score predictions
        const scorePredictionsMap = new Map();
        if (scorePredictionsData && scorePredictionsData.predictions) {
          scorePredictionsData.predictions.forEach(prediction => {
            scorePredictionsMap.set(prediction.fixtureId, {
              homeScorePrediction: prediction.homeScorePrediction,
              awayScorePrediction: prediction.awayScorePrediction
            });
          });
        }

        // Merge predictions with upcoming matches data
        const mergedData = upcomingMatchesData.map(match => {
          // Find corresponding prediction
          const prediction = predictionsData.find(p => p.fixtureId === match.id);

          // Find corresponding score prediction
          const scorePrediction = scorePredictionsMap.get(match.id);

          // Extract the probability values from the prediction
          let homeProbability = 0.5;
          let awayProbability = 0.5;

          if (prediction && prediction.prediction) {
            homeProbability = prediction.prediction.home_win_probability;
            awayProbability = prediction.prediction.away_win_probability;
          }

          // Extract score predictions
          let homeScorePrediction = "N/A";
          let awayScorePrediction = "N/A";

          if (scorePrediction) {
            homeScorePrediction = scorePrediction.homeScorePrediction;
            awayScorePrediction = scorePrediction.awayScorePrediction;
          } else if (prediction && prediction.score_prediction) {
            homeScorePrediction = prediction.score_prediction.home_score;
            awayScorePrediction = prediction.score_prediction.away_score;
          }

          return {
            ...match,
            fixtureId: match.id,
            homeProbability: homeProbability,
            awayProbability: awayProbability,
            homeScorePrediction: homeScorePrediction,
            awayScorePrediction: awayScorePrediction
          };
        });

        // Filter for live matches (started within the last 30 minutes)
        const now = new Date();
        const thirtyMinutesAgo = new Date(now.getTime() - 30 * 60 * 1000);

        const filteredMatches = mergedData.filter(match => {
          // Parse the fixture start time
          const fixtureStart = new Date(match.fixtureStart);

          // Only include matches that have started within the last 30 minutes
          return fixtureStart <= now && fixtureStart >= thirtyMinutesAgo;
        });

        // Sort by most recently started first
        filteredMatches.sort((a, b) => {
          return new Date(b.fixtureStart).getTime() - new Date(a.fixtureStart).getTime();
        });

        setLiveMatches(filteredMatches);
        setError(null);
      } catch (err) {
        setError('Failed to fetch live matches. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchLiveMatches();

    // Set up an interval to refresh the live matches every minute
    const intervalId = setInterval(fetchLiveMatches, 60000);

    // Clean up the interval when the component unmounts
    return () => clearInterval(intervalId);
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading live matches...</p>
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

  if (!liveMatches || liveMatches.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <p className="text-muted-foreground">No live matches available right now.</p>
          <p className="mt-2 text-sm text-muted-foreground">
            Check back later for live matches or view upcoming matches.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
      {liveMatches.map((match) => (
        <LiveMatchCard key={match.fixtureId} match={match} />
      ))}
    </div>
  );
}
