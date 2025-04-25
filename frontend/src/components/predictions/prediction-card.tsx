/**
 * Prediction card component for displaying match predictions.
 */

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar } from "@/components/ui/avatar";
import { format } from "date-fns";

interface PredictionCardProps {
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
    prediction: {
      home_win_probability: number;
      away_win_probability: number;
      predicted_winner: "home" | "away";
      confidence: number;
    };
  };
}

export function PredictionCard({ prediction }: PredictionCardProps) {
  const {
    homePlayer,
    awayPlayer,
    homeTeam,
    awayTeam,
    fixtureStart,
    prediction: predictionData,
  } = prediction;

  const matchDate = new Date(fixtureStart);
  const formattedDate = format(matchDate, "MMM d, yyyy");
  const formattedTime = format(matchDate, "h:mm a");

  const homeWinPercentage = Math.round(predictionData.home_win_probability * 100);
  const awayWinPercentage = Math.round(predictionData.away_win_probability * 100);
  const confidencePercentage = Math.round(predictionData.confidence * 100);

  const isHomeWinner = predictionData.predicted_winner === "home";

  return (
    <Card className={isHomeWinner ? "border-l-4 border-l-green-500" : "border-r-4 border-r-green-500"}>
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
            <span className="text-sm font-bold mt-1">{homeWinPercentage}%</span>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold">VS</div>
            <div className="text-xs text-muted-foreground mt-1">
              Predicted Winner
            </div>
            <div className="text-sm font-semibold mt-1">
              {isHomeWinner ? homePlayer.name : awayPlayer.name}
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
            <span className="text-sm font-bold mt-1">{awayWinPercentage}%</span>
          </div>
        </div>
      </CardContent>
      <CardFooter className="pt-0">
        <div className="w-full text-center">
          <div className="text-xs text-muted-foreground">Confidence</div>
          <div className="text-sm font-semibold">{confidencePercentage}%</div>
        </div>
      </CardFooter>
    </Card>
  );
}
