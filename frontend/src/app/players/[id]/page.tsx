"use client"

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ArrowLeftIcon, BarChartIcon, PersonIcon, CrosshairIcon } from "@radix-ui/react-icons"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { PlayerStats, getPlayerStats } from "@/lib/api"

export default function PlayerDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const playerId = params.id as string
  const [playerData, setPlayerData] = useState<PlayerStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("overview")

  useEffect(() => {
    const fetchPlayerData = async () => {
      setLoading(true)
      try {
        const data = await getPlayerStats()

        if (data[playerId]) {
          setPlayerData(data[playerId])
        } else {
          console.error(`Player with ID ${playerId} not found`)
        }
      } catch (error) {
        console.error('Error fetching player data:', error)
      } finally {
        setLoading(false)
      }
    }

    if (playerId) {
      fetchPlayerData()
    }
  }, [playerId])

  // Calculate favorite team
  const getFavoriteTeam = () => {
    if (!playerData?.teams_used) return { name: "Unknown", matches: 0 }

    let favoriteTeam = { name: "Unknown", matches: 0 }

    Object.entries(playerData.teams_used).forEach(([teamId, teamStats]) => {
      if (teamStats.matches > favoriteTeam.matches) {
        favoriteTeam = {
          name: teamStats.team_name,
          matches: teamStats.matches
        }
      }
    })

    return favoriteTeam
  }

  // Get top opponents
  const getTopOpponents = () => {
    if (!playerData?.opponents_faced) return []

    return Object.entries(playerData.opponents_faced)
      .map(([opponentId, stats]) => ({
        id: opponentId,
        matches: stats.matches,
        wins: stats.wins,
        losses: stats.losses,
        winRate: stats.win_rate,
        avgScore: stats.avg_score,
        avgScoreAgainst: stats.avg_score_against
      }))
      .sort((a, b) => b.matches - a.matches)
      .slice(0, 5)
  }

  // Get teams used
  const getTeamsUsed = () => {
    if (!playerData?.teams_used) return []

    return Object.entries(playerData.teams_used)
      .map(([teamId, stats]) => ({
        id: teamId,
        name: stats.team_name,
        matches: stats.matches,
        wins: stats.wins,
        losses: stats.losses,
        winRate: stats.win_rate,
        avgScore: stats.avg_score
      }))
      .sort((a, b) => b.matches - a.matches)
  }

  // Get recent form
  const getRecentForm = () => {
    if (!playerData?.last_5_matches) return []

    return playerData.last_5_matches.map(match => ({
      opponentId: match.opponent_id,
      opponentName: match.opponent_name,
      teamName: match.team_name,
      score: match.score,
      opponentScore: match.opponent_score,
      win: match.win
    }))
  }

  const favoriteTeam = getFavoriteTeam()
  const topOpponents = getTopOpponents()
  const teamsUsed = getTeamsUsed()
  const recentForm = getRecentForm()

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 container py-6 space-y-6">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.back()}
            className="h-8 w-8"
          >
            <ArrowLeftIcon className="h-4 w-4" />
          </Button>
          <h2 className="text-3xl font-bold tracking-tight">Player Details</h2>
        </div>

        {loading ? (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-4">
                  <Skeleton className="h-16 w-16 rounded-full" />
                  <div className="space-y-2">
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-32" />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[...Array(4)].map((_, i) => (
                    <Skeleton key={i} className="h-16 w-full" />
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[...Array(3)].map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        ) : !playerData ? (
          <div className="flex flex-col items-center justify-center py-12">
            <PersonIcon className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-xl font-medium mb-2">Player Not Found</h3>
            <p className="text-muted-foreground mb-6">The player you're looking for doesn't exist or has been removed.</p>
            <Button onClick={() => router.push('/players')}>
              View All Players
            </Button>
          </div>
        ) : (
          <>
            <Card>
              <CardHeader>
                <div className="flex items-center gap-4">
                  <Avatar className="h-16 w-16">
                    <AvatarFallback>{playerData.player_name.substring(0, 2)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <CardTitle className="text-2xl">{playerData.player_name}</CardTitle>
                    <CardDescription>
                      Favorite Team: {favoriteTeam.name} ({favoriteTeam.matches} matches)
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-card/50 p-4 rounded-lg border border-border">
                    <p className="text-sm text-muted-foreground">Total Matches</p>
                    <p className="text-2xl font-bold">{playerData.total_matches}</p>
                  </div>
                  <div className="bg-card/50 p-4 rounded-lg border border-border">
                    <p className="text-sm text-muted-foreground">Win Rate</p>
                    <p className="text-2xl font-bold">
                      {playerData.total_matches > 0
                        ? Math.round((playerData.wins / playerData.total_matches) * 100)
                        : 0}%
                    </p>
                  </div>
                  <div className="bg-card/50 p-4 rounded-lg border border-border">
                    <p className="text-sm text-muted-foreground">Avg. Score</p>
                    <p className="text-2xl font-bold">
                      {playerData.total_matches > 0
                        ? (playerData.total_score / playerData.total_matches).toFixed(1)
                        : "0.0"}
                    </p>
                  </div>
                  <div className="bg-card/50 p-4 rounded-lg border border-border">
                    <p className="text-sm text-muted-foreground">Record</p>
                    <p className="text-2xl font-bold">{playerData.wins}W - {playerData.losses}L</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Tabs defaultValue="overview" onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="overview">
                  <BarChartIcon className="h-4 w-4 mr-2" />
                  Overview
                </TabsTrigger>
                <TabsTrigger value="teams">
                  <PersonIcon className="h-4 w-4 mr-2" />
                  Teams
                </TabsTrigger>
                <TabsTrigger value="opponents">
                  <CrosshairIcon className="h-4 w-4 mr-2" />
                  Opponents
                </TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="mt-4 space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Form</CardTitle>
                    <CardDescription>Last 5 matches played</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {recentForm.length === 0 ? (
                      <p className="text-muted-foreground text-center py-4">No recent matches found</p>
                    ) : (
                      <div className="space-y-3">
                        {recentForm.map((match, index) => (
                          <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-card/50 border border-border">
                            <div>
                              <div className="font-medium">{match.teamName}</div>
                              <div className="text-sm text-muted-foreground">vs {match.opponentName}</div>
                            </div>
                            <div className="flex items-center gap-3">
                              <div className="text-right">
                                <div className="font-mono font-medium">{match.score} - {match.opponentScore}</div>
                              </div>
                              <Badge
                                variant={match.win ? "default" : "secondary"}
                                className={`w-7 h-7 flex items-center justify-center rounded-full ${
                                  match.win
                                    ? 'bg-green-500/20 text-green-500 hover:bg-green-500/30 border-green-500/30'
                                    : 'bg-red-500/20 text-red-500 hover:bg-red-500/30 border-red-500/30'
                                }`}
                              >
                                {match.win ? 'W' : 'L'}
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Score Distribution</CardTitle>
                    <CardDescription>Points scored in matches</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {!playerData.scores_list || playerData.scores_list.length === 0 ? (
                      <p className="text-muted-foreground text-center py-4">No score data available</p>
                    ) : (
                      <div className="h-48 flex items-end gap-1">
                        {/* Simple histogram of scores */}
                        {(() => {
                          // Group scores into buckets (30-39, 40-49, etc.)
                          const buckets: Record<string, number> = {}
                          playerData.scores_list.forEach(score => {
                            const bucket = Math.floor(score / 10) * 10
                            const bucketLabel = `${bucket}-${bucket + 9}`
                            buckets[bucketLabel] = (buckets[bucketLabel] || 0) + 1
                          })

                          // Find the max count for scaling
                          const maxCount = Math.max(...Object.values(buckets))

                          // Sort buckets by score range
                          return Object.entries(buckets)
                            .sort(([a], [b]) => parseInt(a) - parseInt(b))
                            .map(([range, count]) => {
                              const height = (count / maxCount) * 100
                              return (
                                <div key={range} className="flex flex-col items-center flex-1">
                                  <div
                                    className="w-full bg-primary/70 rounded-t"
                                    style={{ height: `${height}%` }}
                                  ></div>
                                  <div className="text-xs mt-2 text-muted-foreground">{range}</div>
                                  <div className="text-xs font-medium">{count}</div>
                                </div>
                              )
                            })
                        })()}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="teams" className="mt-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Teams Used</CardTitle>
                    <CardDescription>Performance with different teams</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {teamsUsed.length === 0 ? (
                      <p className="text-muted-foreground text-center py-4">No team data available</p>
                    ) : (
                      <div className="space-y-3">
                        {teamsUsed.map(team => (
                          <div key={team.id} className="flex items-center justify-between p-3 rounded-lg bg-card/50 border border-border">
                            <div className="font-medium">{team.name}</div>
                            <div className="flex items-center gap-6">
                              <div className="text-right">
                                <div className="text-sm text-muted-foreground">Matches</div>
                                <div className="font-medium">{team.matches}</div>
                              </div>
                              <div className="text-right">
                                <div className="text-sm text-muted-foreground">Record</div>
                                <div className="font-medium">{team.wins}W - {team.losses}L</div>
                              </div>
                              <div className="text-right">
                                <div className="text-sm text-muted-foreground">Win Rate</div>
                                <div className="font-medium">{Math.round(team.winRate * 100)}%</div>
                              </div>
                              <div className="text-right">
                                <div className="text-sm text-muted-foreground">Avg. Score</div>
                                <div className="font-medium">{team.avgScore.toFixed(1)}</div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="opponents" className="mt-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Top Opponents</CardTitle>
                    <CardDescription>Performance against most frequent opponents</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {topOpponents.length === 0 ? (
                      <p className="text-muted-foreground text-center py-4">No opponent data available</p>
                    ) : (
                      <div className="space-y-3">
                        {topOpponents.map(opponent => (
                          <div key={opponent.id} className="flex items-center justify-between p-3 rounded-lg bg-card/50 border border-border">
                            <div>
                              <div className="font-medium">Player #{opponent.id}</div>
                              <div className="text-sm text-muted-foreground">{opponent.matches} matches</div>
                            </div>
                            <div className="flex items-center gap-6">
                              <div className="text-right">
                                <div className="text-sm text-muted-foreground">Record</div>
                                <div className="font-medium">{opponent.wins}W - {opponent.losses}L</div>
                              </div>
                              <div className="text-right">
                                <div className="text-sm text-muted-foreground">Win Rate</div>
                                <div className="font-medium">{Math.round(opponent.winRate * 100)}%</div>
                              </div>
                              <div className="text-right">
                                <div className="text-sm text-muted-foreground">Avg. Score</div>
                                <div className="font-medium">{opponent.avgScore.toFixed(1)}</div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </>
        )}
      </main>

      <Footer />
    </div>
  )
}
