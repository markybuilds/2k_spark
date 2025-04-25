"use client";

/**
 * Custom hook for fetching prediction statistics.
 */

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api/client';

/**
 * Hook for fetching prediction statistics.
 *
 * @returns Object with statistics data, loading state, and error
 */
export function useStats() {
  const [stats, setStats] = useState<{
    total_matches: number,
    home_wins_predicted: number,
    away_wins_predicted: number,
    avg_confidence: number,
    model_accuracy: number,
    last_updated: string
  } | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getStats();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching stats:', err);
        setError('Failed to fetch statistics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return { stats, loading, error };
}

/**
 * Hook for triggering data refresh.
 *
 * @returns Object with refresh function, loading state, and error
 */
export function useRefresh() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);

  const refreshData = async () => {
    try {
      setLoading(true);
      setSuccess(false);
      setError(null);

      const response = await apiClient.refreshData();

      if (response.status === 'success') {
        setSuccess(true);
      } else {
        setError(response.message || 'Refresh failed');
      }
    } catch (err) {
      console.error('Error refreshing data:', err);
      setError('Failed to refresh data. Please try again later.');
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return { refreshData, loading, error, success };
}
