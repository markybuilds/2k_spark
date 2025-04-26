"use client"

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { MagnifyingGlassIcon } from "@radix-ui/react-icons"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"
import { PlayerStats, getPlayerStats } from "@/lib/api"

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

export default function PlayersPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [players, setPlayers] = useState<ProcessedPlayerData[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '')
  const [filteredPlayers, setFilteredPlayers] = useState<ProcessedPlayerData[]>([])

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
          // Sort by total matches (descending)
          .sort((a, b) => b.totalMatches - a.totalMatches)

        setPlayers(processedPlayers)
        setFilteredPlayers(processedPlayers)
      } catch (error) {
        console.error('Error processing player stats:', error)
        setPlayers([])
        setFilteredPlayers([])
      } finally {
        setLoading(false)
      }
    }

    fetchPlayerStats()
  }, [])

  // Filter players when search query changes
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredPlayers(players)
      return
    }

    const filtered = players.filter(player =>
      player.name.toLowerCase().includes(searchQuery.toLowerCase())
    )
    setFilteredPlayers(filtered)
  }, [searchQuery, players])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // Update URL with search query
    const params = new URLSearchParams(searchParams.toString())
    if (searchQuery) {
      params.set('search', searchQuery)
    } else {
      params.delete('search')
    }
    router.push(`/players?${params.toString()}`)
  }

  const handlePlayerClick = (playerId: number) => {
    router.push(`/players/${playerId}`)
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 container py-6 space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <h2 className="text-3xl font-bold tracking-tight">Players</h2>

          <form onSubmit={handleSearch} className="w-full md:w-auto">
            <div className="flex w-full md:w-[300px]">
              <Input
                type="text"
                placeholder="Search players..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="rounded-r-none"
              />
              <Button type="submit" variant="default" className="rounded-l-none">
                <MagnifyingGlassIcon className="h-4 w-4" />
              </Button>
            </div>
          </form>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            // Loading skeletons
            Array.from({ length: 9 }).map((_, i) => (
              <Card key={i} className="overflow-hidden">
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
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                    <div className="flex gap-1 pt-2">
                      {[...Array(5)].map((_, j) => (
                        <Skeleton key={j} className="h-6 w-6 rounded-full" />
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : filteredPlayers.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <p className="text-muted-foreground">No players found</p>
            </div>
          ) : (
            filteredPlayers.map(player => (
              <Card
                key={player.id}
                className="overflow-hidden cursor-pointer hover:border-primary/50 transition-colors"
                onClick={() => handlePlayerClick(player.id)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-12 w-12">
                      <AvatarFallback>{player.name.substring(0, 2)}</AvatarFallback>
                    </Avatar>
                    <div>
                      <CardTitle className="text-lg">{player.name}</CardTitle>
                      <CardDescription>{player.favoriteTeam}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-2 mb-3">
                    <div>
                      <p className="text-sm text-muted-foreground">Win Rate</p>
                      <p className="font-medium">{Math.round(player.winRate * 100)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Avg. Score</p>
                      <p className="font-medium">{player.avgScore.toFixed(1)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Matches</p>
                      <p className="font-medium">{player.totalMatches}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Record</p>
                      <p className="font-medium">{player.wins}W - {player.losses}L</p>
                    </div>
                  </div>

                  <div className="flex gap-1">
                    <p className="text-sm text-muted-foreground mr-2">Form:</p>
                    {player.recentForm.map((result, index) => (
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
            ))
          )}
        </div>
      </main>

      <Footer />
    </div>
  )
}
