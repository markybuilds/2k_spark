"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { PlayerStats, getPlayerStats } from "@/lib/api"

interface TeamData {
  id: string;
  name: string;
  totalMatches: number;
  wins: number;
  losses: number;
  winRate: number;
  avgScore: number;
  topPlayers: {
    id: string;
    name: string;
    matches: number;
    winRate: number;
  }[];
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<TeamData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchTeamStats = async () => {
      setLoading(true)
      try {
        const playerStatsData = await getPlayerStats()

        // Process player stats to extract team data
        const teamsMap: Record<string, TeamData> = {}

        // Process each player's team data
        Object.entries(playerStatsData).forEach(([playerId, playerData]) => {
          if (!playerData.teams_used) return

          // Process each team used by this player
          Object.entries(playerData.teams_used).forEach(([teamId, teamStats]) => {
            if (!teamsMap[teamId]) {
              teamsMap[teamId] = {
                id: teamId,
                name: teamStats.team_name,
                totalMatches: 0,
                wins: 0,
                losses: 0,
                winRate: 0,
                avgScore: 0,
                topPlayers: []
              }
            }

            // Update team stats
            teamsMap[teamId].totalMatches += teamStats.matches
            teamsMap[teamId].wins += teamStats.wins
            teamsMap[teamId].losses += teamStats.losses

            // Add player to team's top players
            teamsMap[teamId].topPlayers.push({
              id: playerId,
              name: playerData.player_name,
              matches: teamStats.matches,
              winRate: teamStats.win_rate
            })
          })
        })

        // Calculate win rates and sort top players
        Object.values(teamsMap).forEach(team => {
          team.winRate = team.totalMatches > 0 ? team.wins / team.totalMatches : 0
          team.avgScore = team.totalMatches > 0 ?
            (team.topPlayers.reduce((sum, player) => sum + player.matches, 0) / team.totalMatches) : 0

          // Sort top players by matches played
          team.topPlayers.sort((a, b) => b.matches - a.matches)

          // Keep only top 3 players
          team.topPlayers = team.topPlayers.slice(0, 3)
        })

        // Convert to array and sort by total matches
        const teamsArray = Object.values(teamsMap)
          .sort((a, b) => b.totalMatches - a.totalMatches)

        setTeams(teamsArray)
      } catch (error) {
        console.error('Error processing team stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchTeamStats()
  }, [])

  // Function to get team logo URL
  const getTeamLogoUrl = (teamName: string) => {
    // Convert team name to a format that might match the logo files
    const formattedName = teamName
      .toLowerCase()
      .replace(/\s+/g, '_')
      .replace(/[^a-z0-9_]/g, '')

    return `/teams/${formattedName}.png`
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 container py-6 space-y-6">
        <h2 className="text-3xl font-bold tracking-tight">Teams</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            // Loading skeletons
            Array.from({ length: 9 }).map((_, i) => (
              <Card key={i}>
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-3">
                    <Skeleton className="h-12 w-12 rounded-full" />
                    <div>
                      <Skeleton className="h-5 w-32 mb-1" />
                      <Skeleton className="h-4 w-24" />
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                    <Skeleton className="h-16 w-full" />
                  </div>
                  <Skeleton className="h-4 w-full mb-2" />
                  <Skeleton className="h-4 w-full mb-2" />
                  <Skeleton className="h-4 w-full" />
                </CardContent>
              </Card>
            ))
          ) : teams.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-muted-foreground">No team data available</p>
            </div>
          ) : (
            teams.map(team => (
              <Card key={team.id}>
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={getTeamLogoUrl(team.name)} alt={team.name} />
                      <AvatarFallback>{team.name.substring(0, 2)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle className="text-lg">{team.name}</CardTitle>
                      <CardDescription>NBA Team #{team.id}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    <div className="bg-card/50 p-2 rounded-lg border border-border text-center">
                      <p className="text-xs text-muted-foreground">Matches</p>
                      <p className="font-medium">{team.totalMatches}</p>
                    </div>
                    <div className="bg-card/50 p-2 rounded-lg border border-border text-center">
                      <p className="text-xs text-muted-foreground">Win Rate</p>
                      <p className="font-medium">{Math.round(team.winRate * 100)}%</p>
                    </div>
                    <div className="bg-card/50 p-2 rounded-lg border border-border text-center">
                      <p className="text-xs text-muted-foreground">Record</p>
                      <p className="font-medium">{team.wins}W - {team.losses}L</p>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-sm font-medium">Top Players:</p>
                    {team.topPlayers.length === 0 ? (
                      <p className="text-xs text-muted-foreground">No player data available</p>
                    ) : (
                      team.topPlayers.map(player => (
                        <div key={player.id} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Avatar className="h-6 w-6">
                              <AvatarFallback className="text-xs">{player.name.substring(0, 2)}</AvatarFallback>
                            </Avatar>
                            <span className="text-sm">{player.name}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {player.matches} matches
                            </Badge>
                            <Badge
                              variant={player.winRate >= 0.5 ? "default" : "secondary"}
                              className="text-xs"
                            >
                              {Math.round(player.winRate * 100)}% WR
                            </Badge>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </main>

      <Footer />
    </div>
  )
}
