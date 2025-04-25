/**
 * Stats cards component for displaying prediction statistics.
 */

"use client";

import { useStats } from "@/hooks/use-stats";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { format } from "date-fns";

export function StatsCards() {
  const { stats, loading, error } = useStats();

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading statistics...</p>
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

  if (!stats) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <p className="text-muted-foreground">No statistics available.</p>
        </div>
      </div>
    );
  }

  const lastUpdated = new Date(stats.last_updated);
  const formattedLastUpdated = format(lastUpdated, "MMM d, yyyy h:mm a");
  const modelAccuracyPercentage = Math.round(stats.model_accuracy * 100);
  const avgConfidencePercentage = Math.round(stats.avg_confidence * 100);

  return (
    <div className="space-y-6">
      <div className="text-sm text-muted-foreground text-right">
        Last updated: {formattedLastUpdated}
      </div>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Total Matches</CardTitle>
            <CardDescription>
              Upcoming matches with predictions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats.total_matches}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Home Wins</CardTitle>
            <CardDescription>
              Predicted home team victories
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats.home_wins_predicted}</div>
            <div className="text-sm text-muted-foreground">
              {Math.round((stats.home_wins_predicted / stats.total_matches) * 100)}% of matches
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Away Wins</CardTitle>
            <CardDescription>
              Predicted away team victories
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{stats.away_wins_predicted}</div>
            <div className="text-sm text-muted-foreground">
              {Math.round((stats.away_wins_predicted / stats.total_matches) * 100)}% of matches
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">Model Accuracy</CardTitle>
            <CardDescription>
              Historical prediction accuracy
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{modelAccuracyPercentage}%</div>
          </CardContent>
        </Card>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle>Average Confidence</CardTitle>
          <CardDescription>
            Average confidence level for predictions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="w-full bg-muted rounded-full h-4">
            <div 
              className="bg-primary h-4 rounded-full" 
              style={{ width: `${avgConfidencePercentage}%` }}
            ></div>
          </div>
          <div className="mt-2 text-right font-medium">{avgConfidencePercentage}%</div>
        </CardContent>
      </Card>
    </div>
  );
}
