/**
 * History table component for displaying prediction history.
 */

"use client";

import { usePredictionHistory } from "@/hooks/use-predictions";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { format } from "date-fns";
import { useState } from "react";
import { HistoryFilters } from "./history-filters";

export function HistoryTable() {
  const [playerFilter, setPlayerFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("");

  const { history, loading, error } = usePredictionHistory(playerFilter, dateFilter);

  const handleFilterChange = (player: string, date: string) => {
    setPlayerFilter(player);
    setDateFilter(date);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading prediction history...</p>
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

  if (!history || history.length === 0) {
    return (
      <div>
        <HistoryFilters onFilterChange={handleFilterChange} />
        <div className="flex justify-center items-center py-12">
          <div className="text-center">
            <p className="text-muted-foreground">No prediction history available.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <HistoryFilters onFilterChange={handleFilterChange} />

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Date</TableHead>
              <TableHead>Match</TableHead>
              <TableHead>Prediction</TableHead>
              <TableHead>Confidence</TableHead>
              <TableHead>Predicted Score</TableHead>
              <TableHead>Saved At</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {history.map((item) => {
              const matchDate = new Date(item.fixtureStart);
              const formattedDate = format(matchDate, "MMM d, yyyy h:mm a");

              // Handle missing saved_at date
              let formattedSavedDate = "N/A";
              if (item.saved_at) {
                const savedDate = new Date(item.saved_at);
                formattedSavedDate = format(savedDate, "MMM d, yyyy h:mm a");
              } else if (item.generated_at) {
                const generatedDate = new Date(item.generated_at);
                formattedSavedDate = format(generatedDate, "MMM d, yyyy h:mm a");
              }

              const homeWinner = item.prediction.predicted_winner === "home" || item.prediction.predicted_winner === "home_win";
              const confidencePercentage = Math.round(item.prediction.confidence * 100);

              return (
                <TableRow key={`${item.fixtureId}-${item.saved_at}`}>
                  <TableCell>{formattedDate}</TableCell>
                  <TableCell>
                    <div>
                      <div>{item.homePlayer.name} ({item.homeTeam.name})</div>
                      <div>vs</div>
                      <div>{item.awayPlayer.name} ({item.awayTeam.name})</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className={homeWinner ? "text-green-600" : "text-blue-600"}>
                      {homeWinner ? item.homePlayer.name : item.awayPlayer.name}
                    </span>
                  </TableCell>
                  <TableCell>{confidencePercentage}%</TableCell>
                  <TableCell>
                    {item.score_prediction.home_score} - {item.score_prediction.away_score}
                  </TableCell>
                  <TableCell>{formattedSavedDate}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
