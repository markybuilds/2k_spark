"use client";

/**
 * Custom hook for fetching predictions.
 */

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

/**
 * Hook for fetching match predictions.
 *
 * @returns Object with predictions data, loading state, and error
 */
export function usePredictions() {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getPredictions();

        // Filter out matches that have already started
        const now = new Date();

        // Add a buffer time (30 minutes) to include matches that are about to start
        const bufferTime = 30 * 60 * 1000; // 30 minutes in milliseconds
        const cutoffTime = new Date(now.getTime() - bufferTime);

        const upcomingMatches = data.filter(match => {
          // Parse the fixture start time
          const fixtureStart = new Date(match.fixtureStart);

          // Only include matches that haven't started yet (with buffer)
          return fixtureStart > cutoffTime;
        });

        // Sort by start time (earliest first)
        upcomingMatches.sort((a, b) => {
          return new Date(a.fixtureStart).getTime() - new Date(b.fixtureStart).getTime();
        });

        setPredictions(upcomingMatches);
        setError(null);
      } catch (err) {
        console.error('Error fetching predictions:', err);
        setError('Failed to fetch predictions. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
  }, []);

  return { predictions, loading, error };
}

/**
 * Hook for fetching score predictions.
 *
 * @returns Object with score predictions data, model accuracy, loading state, and error
 */
export function useScorePredictions() {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [modelAccuracy, setModelAccuracy] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchScorePredictions = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getScorePredictions();

        // Filter out matches that have already started
        const now = new Date();

        // Add a buffer time (30 minutes) to include matches that are about to start
        const bufferTime = 30 * 60 * 1000; // 30 minutes in milliseconds
        const cutoffTime = new Date(now.getTime() - bufferTime);

        const upcomingMatches = data.predictions.filter(match => {
          // Parse the fixture start time
          const fixtureStart = new Date(match.fixtureStart);

          // Only include matches that haven't started yet (with buffer)
          return fixtureStart > cutoffTime;
        });

        // Sort by start time (earliest first)
        upcomingMatches.sort((a, b) => {
          return new Date(a.fixtureStart).getTime() - new Date(b.fixtureStart).getTime();
        });

        setPredictions(upcomingMatches);
        setModelAccuracy(data.summary.model_accuracy);
        setError(null);
      } catch (err) {
        console.error('Error fetching score predictions:', err);
        setError('Failed to fetch score predictions. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchScorePredictions();
  }, []);

  return { predictions, modelAccuracy, loading, error };
}

/**
 * Hook for fetching prediction history.
 *
 * @param player - Optional player filter
 * @param date - Optional date filter
 * @returns Object with prediction history data, loading state, and error
 */
export function usePredictionHistory(player?: string, date?: string) {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPredictionHistory = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getPredictionHistory(player, date);
        setHistory(data.predictions);
        setError(null);
      } catch (err) {
        console.error('Error fetching prediction history:', err);
        setError('Failed to fetch prediction history. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPredictionHistory();
  }, [player, date]);

  return { history, loading, error };
}

/**
 * Hook for fetching player statistics.
 *
 * @returns Object with player statistics data, loading state, and error
 */
export function usePlayerStats() {
  const [playerStats, setPlayerStats] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlayerStats = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getPlayerStats();
        setPlayerStats(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching player statistics:', err);
        setError('Failed to fetch player statistics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPlayerStats();
  }, []);

  return { playerStats, loading, error };
}

/**
 * Hook for fetching upcoming matches.
 *
 * @returns Object with upcoming matches data, loading state, and error
 */
export function useUpcomingMatches() {
  const [upcomingMatches, setUpcomingMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUpcomingMatches = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getUpcomingMatches();

        // Filter out matches that have already started
        const now = new Date();

        // Add a buffer time (30 minutes) to include matches that are about to start
        const bufferTime = 30 * 60 * 1000; // 30 minutes in milliseconds
        const cutoffTime = new Date(now.getTime() - bufferTime);

        const filteredMatches = data.filter(match => {
          // Parse the fixture start time
          const fixtureStart = new Date(match.fixtureStart);

          // Only include matches that haven't started yet (with buffer)
          return fixtureStart > cutoffTime;
        });

        // Sort by start time (earliest first)
        filteredMatches.sort((a, b) => {
          return new Date(a.fixtureStart).getTime() - new Date(b.fixtureStart).getTime();
        });

        setUpcomingMatches(filteredMatches);
        setError(null);
      } catch (err) {
        console.error('Error fetching upcoming matches:', err);
        setError('Failed to fetch upcoming matches. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchUpcomingMatches();
  }, []);

  return { upcomingMatches, loading, error };
}
