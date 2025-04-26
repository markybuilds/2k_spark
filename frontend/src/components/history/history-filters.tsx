/**
 * History filters component for filtering prediction history.
 */

"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Search, Calendar, FilterX } from "lucide-react";

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
    <Card className="border border-border/50 shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center">
          <div className="bg-primary/10 p-1.5 rounded-md mr-2">
            <Search className="h-4 w-4 text-primary" />
          </div>
          Filter Prediction History
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="player-filter" className="text-sm font-medium flex items-center">
                <Search className="h-3.5 w-3.5 mr-1.5 text-muted-foreground" />
                Player Name
              </Label>
              <div className="relative">
                <Input
                  id="player-filter"
                  placeholder="Enter player name"
                  value={playerFilter}
                  onChange={(e) => setPlayerFilter(e.target.value)}
                  className="pl-8 bg-background/50"
                />
                <Search className="h-4 w-4 absolute left-2.5 top-2.5 text-muted-foreground/70" />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="date-filter" className="text-sm font-medium flex items-center">
                <Calendar className="h-3.5 w-3.5 mr-1.5 text-muted-foreground" />
                Date (YYYY-MM-DD)
              </Label>
              <div className="relative">
                <Input
                  id="date-filter"
                  placeholder="YYYY-MM-DD"
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  className="pl-8 bg-background/50"
                />
                <Calendar className="h-4 w-4 absolute left-2.5 top-2.5 text-muted-foreground/70" />
              </div>
            </div>
          </div>
          <div className="flex justify-end space-x-3 pt-2">
            <Button
              variant="outline"
              type="button"
              onClick={handleReset}
              className="flex items-center"
              size="sm"
            >
              <FilterX className="h-4 w-4 mr-1.5" />
              Reset
            </Button>
            <Button
              type="submit"
              className="flex items-center"
              size="sm"
            >
              <Search className="h-4 w-4 mr-1.5" />
              Apply Filters
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
