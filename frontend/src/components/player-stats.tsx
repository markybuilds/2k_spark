"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { PlayerStats as PlayerStatsType, getPlayerStats } from "@/lib/api"

// Type for our processed player data
interface ProcessedPlayerData {
  id: number;
  name: string;
  totalMatches: number;
  wins: number;
  losses: number;
  winRate: number;
  avgScore: number;
  favoriteTeam: string;
  recentForm: ('W' | 'L')[];
}

export function PlayerStats() {
  const [activeTab, setActiveTab] = useState("top-players")
  const [players, setPlayers] = useState<ProcessedPlayerData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPlayerStats = async () => {
      setLoading(true)
      try {
        const data = await getPlayerStats()

        // Check if we have data
        if (Object.keys(data).length === 0) {
          console.warn('No player stats data available')
          setPlayers([])
          setLoading(false)
          return
        }

        // Process the raw player stats into the format we need
        const processedPlayers = Object.entries(data)
          .map(([id, stats]) => {
            // Find favorite team (team with most matches)
            let favoriteTeam = "Unknown"
            let maxMatches = 0

            // Check if teams_used exists and is not empty
            if (stats.teams_used && Object.keys(stats.teams_used).length > 0) {
              Object.entries(stats.teams_used).forEach(([teamId, teamStats]) => {
                if (teamStats.matches > maxMatches) {
                  maxMatches = teamStats.matches
                  favoriteTeam = teamStats.team_name
                }
              })
            }

            // Calculate average score
            const avgScore = stats.total_matches > 0
              ? stats.total_score / stats.total_matches
              : 0

            // Extract recent form from last 5 matches
            const recentForm: ('W' | 'L')[] = []

            // Check if last_5_matches exists and is not empty
            if (stats.last_5_matches && stats.last_5_matches.length > 0) {
              stats.last_5_matches.forEach(match => {
                if (typeof match.win === 'boolean') {
                  recentForm.push(match.win ? 'W' : 'L')
                }
              })
            }

            // Fill with 'L' if we don't have enough matches
            while (recentForm.length < 5) {
              recentForm.push('L')
            }

            return {
              id: typeof stats.player_id === 'number' ? stats.player_id : parseInt(id),
              name: stats.player_name || `Player ${id}`,
              totalMatches: stats.total_matches || 0,
              wins: stats.wins || 0,
              losses: stats.losses || 0,
              winRate: stats.total_matches > 0 ? stats.wins / stats.total_matches : 0,
              avgScore,
              favoriteTeam,
              recentForm: recentForm.slice(0, 5)
            }
          })
          // Filter out players with no matches
          .filter(player => player.totalMatches > 0)
          // Sort by win rate (descending)
          .sort((a, b) => b.winRate - a.winRate)
          // Take top 5 players
          .slice(0, 5)

        setPlayers(processedPlayers)
      } catch (error) {
        console.error('Error processing player stats:', error)
        setPlayers([])
      } finally {
        setLoading(false)
      }
    }

    fetchPlayerStats()
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Player Statistics</CardTitle>
        <CardDescription>
          Performance data for top players in the league
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="top-players" onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="top-players">Top Players</TabsTrigger>
            <TabsTrigger value="form-guide">Form Guide</TabsTrigger>
          </TabsList>

          <TabsContent value="top-players" className="mt-4">
            {loading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-card/50 border border-border">
                    <div className="flex items-center gap-3">
                      <Skeleton className="h-10 w-10 rounded-full" />
                      <div>
                        <Skeleton className="h-5 w-24" />
                        <Skeleton className="h-3 w-16 mt-1" />
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <Skeleton className="h-8 w-20" />
                      <Skeleton className="h-8 w-16" />
                    </div>
                  </div>
                ))}
              </div>
            ) : players.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground">
                No player statistics available
              </div>
            ) : (
              <div className="space-y-4">
                {players.map(player => (
                  <div key={player.id} className="flex items-center justify-between p-3 rounded-lg bg-card/50 border border-border">
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarFallback>{player.name.substring(0, 2)}</AvatarFallback>
                      </Avatar>
                      <div>
                        <div className="font-medium">{player.name}</div>
                        <div className="text-xs text-muted-foreground">{player.favoriteTeam}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className="text-sm font-medium">{player.wins}W - {player.losses}L</div>
                        <div className="text-xs text-muted-foreground">
                          {Math.round(player.winRate * 100)}% Win Rate
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">{player.avgScore.toFixed(1)}</div>
                        <div className="text-xs text-muted-foreground">Avg. Score</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="form-guide" className="mt-4">
            {loading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-card/50 border border-border">
                    <div className="flex items-center gap-3">
                      <Skeleton className="h-10 w-10 rounded-full" />
                      <Skeleton className="h-5 w-24" />
                    </div>
                    <div className="flex items-center gap-2">
                      {[...Array(5)].map((_, j) => (
                        <Skeleton key={j} className="h-7 w-7 rounded-full" />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : players.length === 0 ? (
              <div className="text-center py-6 text-muted-foreground">
                No player statistics available
              </div>
            ) : (
              <div className="space-y-4">
                {players.map(player => (
                  <div key={player.id} className="flex items-center justify-between p-3 rounded-lg bg-card/50 border border-border">
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarFallback>{player.name.substring(0, 2)}</AvatarFallback>
                      </Avatar>
                      <div className="font-medium">{player.name}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      {player.recentForm.map((result, index) => (
                        <Badge
                          key={index}
                          variant={result === 'W' ? 'default' : 'secondary'}
                          className={`w-7 h-7 flex items-center justify-center rounded-full ${
                            result === 'W'
                              ? 'bg-green-500/20 text-green-500 hover:bg-green-500/30 border-green-500/30'
                              : 'bg-red-500/20 text-red-500 hover:bg-red-500/30 border-red-500/30'
                          }`}
                        >
                          {result}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
