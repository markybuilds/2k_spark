/**
 * History filters component for filtering prediction history.
 */

"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface HistoryFiltersProps {
  onFilterChange: (player: string, date: string) => void;
}

export function HistoryFilters({ onFilterChange }: HistoryFiltersProps) {
  const [playerFilter, setPlayerFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilterChange(playerFilter, dateFilter);
  };

  const handleReset = () => {
    setPlayerFilter("");
    setDateFilter("");
    onFilterChange("", "");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-muted rounded-lg">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="player-filter">Player Name</Label>
          <Input
            id="player-filter"
            placeholder="Filter by player name"
            value={playerFilter}
            onChange={(e) => setPlayerFilter(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="date-filter">Date (YYYY-MM-DD)</Label>
          <Input
            id="date-filter"
            placeholder="Filter by date"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
          />
        </div>
      </div>
      <div className="flex justify-end space-x-2">
        <Button variant="outline" type="button" onClick={handleReset}>
          Reset
        </Button>
        <Button type="submit">
          Apply Filters
        </Button>
      </div>
    </form>
  );
}
