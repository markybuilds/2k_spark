/**
 * Match card component for displaying an upcoming match.
 */

"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { formatDate } from "@/lib/utils";

interface MatchCardProps {
  match: any;
}

export function MatchCard({ match }: MatchCardProps) {
  const { homePlayer, awayPlayer, homeTeam, awayTeam, fixtureStart } = match;

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-muted/50 pb-2">
        <CardTitle className="text-sm font-medium flex justify-between items-center">
          <span>Upcoming Match</span>
          <span className="text-xs text-muted-foreground">
            {formatDate(fixtureStart)}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4">
        <div className="flex justify-between items-center">
          <div className="flex flex-col items-center text-center space-y-2 flex-1">
            <Avatar className="h-16 w-16 border-2 border-primary">
              <AvatarFallback>{homePlayer?.name?.charAt(0) || "H"}</AvatarFallback>
              <AvatarImage src={`/avatars/${homePlayer?.id || "default"}.png`} />
            </Avatar>
            <div>
              <p className="font-bold">{homePlayer?.name || "Home Player"}</p>
              <p className="text-xs text-muted-foreground">{homeTeam?.name || "Home Team"}</p>
            </div>
          </div>

          <div className="flex flex-col items-center px-4">
            <span className="text-xl font-bold">VS</span>
          </div>

          <div className="flex flex-col items-center text-center space-y-2 flex-1">
            <Avatar className="h-16 w-16 border-2 border-primary">
              <AvatarFallback>{awayPlayer?.name?.charAt(0) || "A"}</AvatarFallback>
              <AvatarImage src={`/avatars/${awayPlayer?.id || "default"}.png`} />
            </Avatar>
            <div>
              <p className="font-bold">{awayPlayer?.name || "Away Player"}</p>
              <p className="text-xs text-muted-foreground">{awayTeam?.name || "Away Team"}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
