/**
 * Score card component for displaying score predictions.
 */

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar } from "@/components/ui/avatar";
import { format } from "date-fns";

interface ScoreCardProps {
  prediction: {
    fixtureId: string;
    homePlayer: {
      id: string;
      name: string;
    };
    awayPlayer: {
      id: string;
      name: string;
    };
    homeTeam: {
      id: string;
      name: string;
    };
    awayTeam: {
      id: string;
      name: string;
    };
    fixtureStart: string;
    score_prediction: {
      home_score: number;
      away_score: number;
      total_score: number;
      score_diff: number;
    };
  };
}

export function ScoreCard({ prediction }: ScoreCardProps) {
  const {
    homePlayer,
    awayPlayer,
    homeTeam,
    awayTeam,
    fixtureStart,
    score_prediction,
  } = prediction;

  const matchDate = new Date(fixtureStart);
  const formattedDate = format(matchDate, "MMM d, yyyy");
  const formattedTime = format(matchDate, "h:mm a");

  const homeWinner = score_prediction.home_score > score_prediction.away_score;
  const scoreDiff = Math.abs(score_prediction.score_diff);

  return (
    <Card className={homeWinner ? "border-l-4 border-l-blue-500" : "border-r-4 border-r-blue-500"}>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex justify-between">
          <span>{homeTeam.name} vs {awayTeam.name}</span>
        </CardTitle>
        <CardDescription>
          {formattedDate} at {formattedTime}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-center mb-4">
          <div className="flex flex-col items-center">
            <Avatar className="h-12 w-12 mb-2">
              <div className="flex h-full w-full items-center justify-center bg-muted font-semibold">
                {homePlayer.name.substring(0, 2)}
              </div>
            </Avatar>
            <span className="text-sm font-medium">{homePlayer.name}</span>
            <span className="text-xs text-muted-foreground">{homeTeam.name}</span>
            <span className="text-xl font-bold mt-1">{score_prediction.home_score}</span>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold">-</div>
            <div className="text-xs text-muted-foreground mt-1">
              Predicted Score
            </div>
            <div className="text-sm font-semibold mt-1">
              Diff: {scoreDiff} pts
            </div>
          </div>

          <div className="flex flex-col items-center">
            <Avatar className="h-12 w-12 mb-2">
              <div className="flex h-full w-full items-center justify-center bg-muted font-semibold">
                {awayPlayer.name.substring(0, 2)}
              </div>
            </Avatar>
            <span className="text-sm font-medium">{awayPlayer.name}</span>
            <span className="text-xs text-muted-foreground">{awayTeam.name}</span>
            <span className="text-xl font-bold mt-1">{score_prediction.away_score}</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="pt-0">
        <div className="w-full text-center">
          <div className="text-xs text-muted-foreground">Total Score</div>
          <div className="text-sm font-semibold">{score_prediction.total_score} points</div>
        </div>
      </CardFooter>
    </Card>
  );
}
