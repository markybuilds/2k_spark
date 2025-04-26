/**
 * Live match card component for displaying a live match with predictions.
 */

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { formatDistanceToNow } from "date-fns";

interface LiveMatchCardProps {
  match: any;
}

export function LiveMatchCard({ match }: LiveMatchCardProps) {
  // Format the match start time
  const matchStartTime = new Date(match.fixtureStart);
  const timeAgo = formatDistanceToNow(matchStartTime, { addSuffix: true });

  // Calculate elapsed time in minutes
  const now = new Date();
  const elapsedMinutes = Math.floor((now.getTime() - matchStartTime.getTime()) / (1000 * 60));

  // Determine the predicted winner
  const homeWinProbability = match.homeProbability || match.homeWinProbability || 0;
  const awayWinProbability = match.awayProbability || match.awayWinProbability || 0;

  const predictedWinner = homeWinProbability > awayWinProbability ? match.homePlayer : match.awayPlayer;
  const winnerConfidence = Math.max(homeWinProbability, awayWinProbability) * 100;

  // Get score predictions if available
  const homeScorePrediction = match.homeScorePrediction || "N/A";
  const awayScorePrediction = match.awayScorePrediction || "N/A";
  const totalScore = match.totalScore || "N/A";
  const scoreDiff = match.scoreDiff || "N/A";

  // Debug the score predictions
  console.log('Match score predictions:', {
    matchId: match.fixtureId,
    homeScorePrediction,
    awayScorePrediction,
    totalScore,
    scoreDiff,
    rawHomeScore: match.rawHomeScore,
    rawAwayScore: match.rawAwayScore,
    rawTotalScore: match.rawTotalScore,
    rawScoreDiff: match.rawScoreDiff
  });

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-muted p-4">
        <div className="flex justify-between items-center">
          <Badge variant="outline" className="bg-red-500 text-white">LIVE</Badge>
          <span className="text-sm text-muted-foreground">Started {timeAgo} ({elapsedMinutes} min)</span>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        {/* Players */}
        <div className="flex justify-between items-center mb-6">
          {/* Home Player */}
          <div className="flex flex-col items-center text-center space-y-2">
            <Avatar className="h-16 w-16">
              <AvatarImage src={`/avatars/${match.homePlayer.id}.png`} alt={match.homePlayer.name} />
              <AvatarFallback>{match.homePlayer.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold">{match.homePlayer.name}</p>
              <p className="text-sm text-muted-foreground">Home</p>
            </div>
          </div>

          {/* VS */}
          <div className="flex flex-col items-center">
            <p className="text-xl font-bold">VS</p>
            <p className="text-sm text-muted-foreground">Match #{match.fixtureId}</p>
          </div>

          {/* Away Player */}
          <div className="flex flex-col items-center text-center space-y-2">
            <Avatar className="h-16 w-16">
              <AvatarImage src={`/avatars/${match.awayPlayer.id}.png`} alt={match.awayPlayer.name} />
              <AvatarFallback>{match.awayPlayer.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <div>
              <p className="font-semibold">{match.awayPlayer.name}</p>
              <p className="text-sm text-muted-foreground">Away</p>
            </div>
          </div>
        </div>

        {/* Predictions */}
        <div className="space-y-4">
          {/* Winner Prediction */}
          <div className="bg-muted p-3 rounded-md">
            <p className="text-sm font-medium mb-1">Predicted Winner</p>
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <Avatar className="h-6 w-6">
                  <AvatarImage src={`/avatars/${predictedWinner.id}.png`} alt={predictedWinner.name} />
                  <AvatarFallback>{predictedWinner.name.charAt(0)}</AvatarFallback>
                </Avatar>
                <span>{predictedWinner.name}</span>
              </div>
              <Badge variant="outline" className="bg-primary/10">
                {winnerConfidence.toFixed(0)}% confidence
              </Badge>
            </div>
          </div>

          {/* Score Prediction - Always show this section for debugging */}
            <div className="bg-muted p-3 rounded-md">
              <p className="text-sm font-medium mb-1">Predicted Score</p>
              <div className="flex justify-center items-center mb-2">
                <div className="flex items-center space-x-4">
                  <div className="text-center">
                    <p className="text-lg font-bold">{homeScorePrediction}</p>
                    <p className="text-xs text-muted-foreground">Home</p>
                  </div>
                  <span className="text-lg">-</span>
                  <div className="text-center">
                    <p className="text-lg font-bold">{awayScorePrediction}</p>
                    <p className="text-xs text-muted-foreground">Away</p>
                  </div>
                </div>
              </div>

              {/* Total Score */}
              <div className="flex justify-center items-center mt-2 pt-2 border-t border-border/30">
                <div className="flex items-center space-x-6">
                  <div className="text-center">
                    <p className="text-sm font-medium">Total</p>
                    <p className="text-base font-bold">{totalScore}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-medium">Spread</p>
                    <p className="text-base font-bold">{scoreDiff}</p>
                  </div>
                </div>
              </div>
            </div>
        </div>
      </CardContent>
    </Card>
  );
}
