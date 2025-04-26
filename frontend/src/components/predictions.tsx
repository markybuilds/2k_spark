"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Skeleton } from "@/components/ui/skeleton"
import { Prediction, getPredictions } from "@/lib/api"

export function Predictions() {
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPredictions = async () => {
      setLoading(true)
      try {
        const data = await getPredictions()
        setPredictions(data)
      } catch (error) {
        console.error('Error fetching predictions:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchPredictions()
  }, [])

  // Format date to a more readable format
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  // Format confidence as percentage
  const formatConfidence = (confidence: number) => {
    return `${Math.round(confidence * 100)}%`
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Match Predictions</CardTitle>
        <CardDescription>
          AI-powered predictions for upcoming matches
        </CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : predictions.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            No predictions available
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Match</TableHead>
                <TableHead>Prediction</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Confidence</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {predictions.slice(0, 10).map((prediction, idx) => (
                // Use prediction.id if available, otherwise fallback to index
                <TableRow key={prediction.fixtureId ?? `idx-${idx}`}>
                  <TableCell>
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-1 text-sm">
                        <span className="font-medium">{prediction.homePlayer.name}</span>
                        <span className="text-xs text-muted-foreground">vs</span>
                        <span className="font-medium">{prediction.awayPlayer.name}</span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatDate(prediction.fixtureStart)}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant={prediction.prediction?.predicted_winner === 'home' ? 'default' : 'secondary'}
                      className="font-medium"
                    >
                      {prediction.prediction?.predicted_winner === 'home' 
                        ? prediction.homePlayer.name 
                        : prediction.awayPlayer.name}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="font-mono">
                      {typeof prediction.score_prediction?.home_score === 'number' && typeof prediction.score_prediction?.away_score === 'number' 
                        ? `${prediction.score_prediction.home_score} - ${prediction.score_prediction.away_score}` 
                        : '-'}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div 
                      className={`text-sm font-medium ${
                        prediction.confidence > 0.7 
                          ? 'text-green-500 dark:text-green-400' 
                          : prediction.confidence > 0.5 
                            ? 'text-yellow-500 dark:text-yellow-400' 
                            : 'text-red-500 dark:text-red-400'
                      }`}
                    >
                      {typeof prediction.prediction?.confidence === 'number' 
                        ? formatConfidence(prediction.prediction.confidence) 
                        : '-'}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}
