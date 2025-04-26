"use client"

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ArrowRightIcon, ReloadIcon } from "@radix-ui/react-icons"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { PlayerStats, getPlayerStats } from "@/lib/api"

interface ProcessedPlayerData {
  id: string;
  name: string;
  totalMatches: number;
  wins: number;
  losses: number;
  winRate: number;
  avgScore: number;
  favoriteTeam: string;
  recentForm: ('W' | 'L')[];
}

export default function ComparePage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [allPlayers, setAllPlayers] = useState<ProcessedPlayerData[]>([])
  const [player1Id, setPlayer1Id] = useState<string>(searchParams.get('player1') || '')
  const [player2Id, setPlayer2Id] = useState<string>(searchParams.get('player2') || '')
  const [player1Data, setPlayer1Data] = useState<ProcessedPlayerData | null>(null)
  const [player2Data, setPlayer2Data] = useState<ProcessedPlayerData | null>(null)
  const [headToHead, setHeadToHead] = useState<{
    matches: number;
    player1Wins: number;
    player2Wins: number;
    player1AvgScore: number;
    player2AvgScore: number;
  } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchPlayerStats = async () => {
      setLoading(true)
      try {
        const data = await getPlayerStats()

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
              id,
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
          // Sort by name
          .sort((a, b) => a.name.localeCompare(b.name))

        setAllPlayers(processedPlayers)

        // Set player data if IDs are provided
        if (player1Id) {
          const player1 = processedPlayers.find(p => p.id === player1Id)
          if (player1) setPlayer1Data(player1)
        }

        if (player2Id) {
          const player2 = processedPlayers.find(p => p.id === player2Id)
          if (player2) setPlayer2Data(player2)
        }

        // Calculate head-to-head stats if both players are selected
        if (player1Id && player2Id) {
          calculateHeadToHead(data, player1Id, player2Id)
        }
      } catch (error) {
        console.error('Error processing player stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchPlayerStats()
  }, [player1Id, player2Id])

  const calculateHeadToHead = (data: Record<string, PlayerStats>, player1Id: string, player2Id: string) => {
    const player1 = data[player1Id]
    const player2 = data[player2Id]

    if (!player1 || !player2 || !player1.opponents_faced || !player2.opponents_faced) {
      setHeadToHead(null)
      return
    }

    // Check if players have faced each other
    const player1VsPlayer2 = player1.opponents_faced[player2Id]
    const player2VsPlayer1 = player2.opponents_faced[player1Id]

    if (!player1VsPlayer2 && !player2VsPlayer1) {
      setHeadToHead(null)
      return
    }

    // Calculate head-to-head stats
    const matches = player1VsPlayer2 ? player1VsPlayer2.matches : (player2VsPlayer1 ? player2VsPlayer1.matches : 0)
    const player1Wins = player1VsPlayer2 ? player1VsPlayer2.wins : (player2VsPlayer1 ? player2VsPlayer1.losses : 0)
    const player2Wins = player2VsPlayer1 ? player2VsPlayer1.wins : (player1VsPlayer2 ? player1VsPlayer2.losses : 0)
    const player1AvgScore = player1VsPlayer2 ? player1VsPlayer2.avg_score : 0
    const player2AvgScore = player2VsPlayer1 ? player2VsPlayer1.avg_score : 0

    setHeadToHead({
      matches,
      player1Wins,
      player2Wins,
      player1AvgScore,
      player2AvgScore
    })
  }

  const handlePlayer1Change = (value: string) => {
    setPlayer1Id(value)
    updateUrl(value, player2Id)
  }

  const handlePlayer2Change = (value: string) => {
    setPlayer2Id(value)
    updateUrl(player1Id, value)
  }

  const updateUrl = (p1: string, p2: string) => {
    const params = new URLSearchParams()
    if (p1) params.set('player1', p1)
    if (p2) params.set('player2', p2)
    router.push(`/compare?${params.toString()}`)
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 container py-6 space-y-6">
        <h2 className="text-3xl font-bold tracking-tight">Head-to-Head Comparison</h2>

        <Card>
          <CardHeader>
            <CardTitle>Select Players to Compare</CardTitle>
            <CardDescription>
              Choose two players to see their head-to-head statistics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row items-center gap-4">
              <div className="w-full md:w-2/5">
                <Select value={player1Id} onValueChange={handlePlayer1Change}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Player 1" />
                  </SelectTrigger>
                  <SelectContent>
                    {allPlayers.map(player => (
                      <SelectItem key={player.id} value={player.id}>
                        {player.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-center">
                <ArrowRightIcon className="h-6 w-6 text-muted-foreground" />
              </div>

              <div className="w-full md:w-2/5">
                <Select value={player2Id} onValueChange={handlePlayer2Change}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Player 2" />
                  </SelectTrigger>
                  <SelectContent>
                    {allPlayers.map(player => (
                      <SelectItem key={player.id} value={player.id}>
                        {player.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Skeleton className="h-64 w-full" />
            <Skeleton className="h-64 w-full" />
          </div>
        ) : player1Data && player2Data ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarFallback>{player1Data.name.substring(0, 2)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle>{player1Data.name}</CardTitle>
                      <CardDescription>{player1Data.favoriteTeam}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-card/50 p-3 rounded-lg border border-border">
                      <p className="text-sm text-muted-foreground">Win Rate</p>
                      <p className="text-xl font-bold">{Math.round(player1Data.winRate * 100)}%</p>
                    </div>
                    <div className="bg-card/50 p-3 rounded-lg border border-border">
                      <p className="text-sm text-muted-foreground">Avg. Score</p>
                      <p className="text-xl font-bold">{player1Data.avgScore.toFixed(1)}</p>
                    </div>
                    <div className="bg-card/50 p-3 rounded-lg border border-border">
                      <p className="text-sm text-muted-foreground">Total Matches</p>
                      <p className="text-xl font-bold">{player1Data.totalMatches}</p>
                    </div>
                    <div className="bg-card/50 p-3 rounded-lg border border-border">
                      <p className="text-sm text-muted-foreground">Record</p>
                      <p className="text-xl font-bold">{player1Data.wins}W - {player1Data.losses}L</p>
                    </div>
                  </div>

                  <div className="flex gap-1 items-center">
                    <p className="text-sm text-muted-foreground mr-2">Recent Form:</p>
                    {player1Data.recentForm.map((result, index) => (
                      <Badge
                        key={index}
                        variant={result === 'W' ? 'default' : 'secondary'}
                        className={`w-6 h-6 flex items-center justify-center rounded-full ${
                          result === 'W'
                            ? 'bg-green-500/20 text-green-500 hover:bg-green-500/30 border-green-500/30'
                            : 'bg-red-500/20 text-red-500 hover:bg-red-500/30 border-red-500/30'
                        }`}
                      >
                        {result}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarFallback>{player2Data.name.substring(0, 2)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle>{player2Data.name}</CardTitle>
                      <CardDescription>{player2Data.favoriteTeam}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-card/50 p-3 rounded-lg border border-border">
                      <p className="text-sm text-muted-foreground">Win Rate</p>
                      <p className="text-xl font-bold">{Math.round(player2Data.winRate * 100)}%</p>
                    </div>
                    <div className="bg-card/50 p-3 rounded-lg border border-border">
                      <p className="text-sm text-muted-foreground">Avg. Score</p>
                      <p className="text-xl font-bold">{player2Data.avgScore.toFixed(1)}</p>
                    </div>
                    <div className="bg-card/50 p-3 rounded-lg border border-border">
                      <p className="text-sm text-muted-foreground">Total Matches</p>
                      <p className="text-xl font-bold">{player2Data.totalMatches}</p>
                    </div>
                    <div className="bg-card/50 p-3 rounded-lg border border-border">
                      <p className="text-sm text-muted-foreground">Record</p>
                      <p className="text-xl font-bold">{player2Data.wins}W - {player2Data.losses}L</p>
                    </div>
                  </div>

                  <div className="flex gap-1 items-center">
                    <p className="text-sm text-muted-foreground mr-2">Recent Form:</p>
                    {player2Data.recentForm.map((result, index) => (
                      <Badge
                        key={index}
                        variant={result === 'W' ? 'default' : 'secondary'}
                        className={`w-6 h-6 flex items-center justify-center rounded-full ${
                          result === 'W'
                            ? 'bg-green-500/20 text-green-500 hover:bg-green-500/30 border-green-500/30'
                            : 'bg-red-500/20 text-red-500 hover:bg-red-500/30 border-red-500/30'
                        }`}
                      >
                        {result}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Head-to-Head Statistics</CardTitle>
                <CardDescription>
                  Direct comparison between {player1Data.name} and {player2Data.name}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!headToHead ? (
                  <div className="text-center py-6">
                    <p className="text-muted-foreground mb-4">These players haven't faced each other yet.</p>
                    <Button variant="outline" disabled>
                      <ReloadIcon className="mr-2 h-4 w-4" />
                      Check Again
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="flex items-center justify-center gap-4">
                      <div className="text-center">
                        <Avatar className="h-16 w-16 mx-auto mb-2">
                          <AvatarFallback>{player1Data.name.substring(0, 2)}</AvatarFallback>
                        </Avatar>
                        <p className="font-medium">{player1Data.name}</p>
                      </div>

                      <div className="text-center bg-card/50 p-4 rounded-lg border border-border">
                        <p className="text-sm text-muted-foreground">Total Matches</p>
                        <p className="text-3xl font-bold">{headToHead.matches}</p>
                      </div>

                      <div className="text-center">
                        <Avatar className="h-16 w-16 mx-auto mb-2">
                          <AvatarFallback>{player2Data.name.substring(0, 2)}</AvatarFallback>
                        </Avatar>
                        <p className="font-medium">{player2Data.name}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-card/50 p-3 rounded-lg border border-border text-center">
                        <p className="text-sm text-muted-foreground">Wins</p>
                        <p className="text-xl font-bold">{headToHead.player1Wins}</p>
                      </div>

                      <div className="bg-card/50 p-3 rounded-lg border border-border text-center">
                        <p className="text-sm text-muted-foreground">Win Rate</p>
                        <p className="text-xl font-bold">
                          {headToHead.player1Wins > headToHead.player2Wins ? (
                            <span className="text-green-500">{player1Data.name}</span>
                          ) : headToHead.player2Wins > headToHead.player1Wins ? (
                            <span className="text-green-500">{player2Data.name}</span>
                          ) : (
                            "Tied"
                          )}
                        </p>
                      </div>

                      <div className="bg-card/50 p-3 rounded-lg border border-border text-center">
                        <p className="text-sm text-muted-foreground">Wins</p>
                        <p className="text-xl font-bold">{headToHead.player2Wins}</p>
                      </div>

                      <div className="bg-card/50 p-3 rounded-lg border border-border text-center">
                        <p className="text-sm text-muted-foreground">Avg. Score</p>
                        <p className="text-xl font-bold">{headToHead.player1AvgScore.toFixed(1)}</p>
                      </div>

                      <div className="bg-card/50 p-3 rounded-lg border border-border text-center">
                        <p className="text-sm text-muted-foreground">Score Diff</p>
                        <p className="text-xl font-bold">
                          {(headToHead.player1AvgScore - headToHead.player2AvgScore).toFixed(1)}
                        </p>
                      </div>

                      <div className="bg-card/50 p-3 rounded-lg border border-border text-center">
                        <p className="text-sm text-muted-foreground">Avg. Score</p>
                        <p className="text-xl font-bold">{headToHead.player2AvgScore.toFixed(1)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Select two players to compare their statistics</p>
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
