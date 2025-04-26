/**
 * Predictions page for displaying match predictions.
 */

"use client";

import { PredictionList } from "@/components/predictions/prediction-list";
import { ContentLayout, PageHeader } from "@/components/layout/content-layout";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api/client";
import { Button } from "@/components/ui/button";

export default function PredictionsPage() {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Log when the component mounts
  useEffect(() => {
    console.log("PredictionsPage mounted");

    // Try to fetch predictions on mount
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      console.log("Directly fetching predictions...");

      // Add a timestamp to prevent caching
      const timestamp = Date.now();
      console.log(`Using timestamp: ${timestamp}`);

      // Make the API request with fetch directly
      const response = await fetch(`http://localhost:5000/api/predictions?timestamp=${timestamp}`);

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const data = await response.json();

      // Check if the data is in the expected format
      if (Array.isArray(data)) {
        console.log("Direct API response (array format):", JSON.stringify(data).substring(0, 200) + "...");
        console.log(`Fetched ${data.length} predictions directly (array format)`);

        // Debug: Log the first prediction
        if (data.length > 0) {
          console.log('First prediction:', JSON.stringify(data[0]).substring(0, 200) + '...');
        }

        setPredictions(data);
      } else if (data && typeof data === 'object' && Array.isArray(data.predictions)) {
        // Handle object format with predictions array
        console.log("Direct API response (object format):", JSON.stringify(data).substring(0, 200) + "...");
        console.log(`Fetched ${data.predictions.length} predictions directly (object format)`);

        // Debug: Log the first prediction
        if (data.predictions.length > 0) {
          console.log('First prediction:', JSON.stringify(data.predictions[0]).substring(0, 200) + '...');
        }

        setPredictions(data.predictions);
      } else {
        console.error("Unexpected API response format:", data);
        setError("Unexpected API response format");
        setPredictions([]);
      }

      setError(null);
    } catch (err) {
      console.error("Error directly fetching predictions:", err);
      setError(`Failed to fetch predictions directly: ${err.message}`);
      setPredictions([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ContentLayout>
      <PageHeader
        title="Match Predictions"
        description="View predictions for upcoming NBA 2K25 eSports matches."
      />

      <div className="mb-8 p-4 border rounded-md">
        <h2 className="text-xl font-bold mb-4">Debug Panel</h2>
        <Button onClick={fetchPredictions} disabled={loading}>
          {loading ? "Loading..." : "Fetch Predictions Directly"}
        </Button>
        {error && <p className="text-red-500 mt-2">{error}</p>}
        <div className="mt-4">
          <p>Predictions count: {predictions.length}</p>
          {predictions.length > 0 && (
            <div className="mt-2 p-2 bg-muted rounded-md">
              <p className="font-semibold">First prediction:</p>
              <pre className="text-xs overflow-auto mt-1">
                {JSON.stringify(predictions[0], null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>

      <PredictionList />
    </ContentLayout>
  );
}
