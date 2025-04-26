"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Skeleton } from "@/components/ui/skeleton"
import { Match, getUpcomingMatches } from "@/lib/api"

export function UpcomingMatches() {
  const [matches, setMatches] = useState<Match[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMatches = async () => {
      setLoading(true)
      try {
        const data = await getUpcomingMatches()
        setMatches(data)
      } catch (error) {
        console.error('Error fetching upcoming matches:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMatches()
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

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upcoming Matches</CardTitle>
        <CardDescription>
          Next scheduled matches in the H2H GG League
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
        ) : matches.length === 0 ? (
          <div className="text-center py-6 text-muted-foreground">
            No upcoming matches found
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Home</TableHead>
                <TableHead>Away</TableHead>
                <TableHead>Teams</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {matches.slice(0, 10).map((match) => (
                <TableRow key={match.id}>
                  <TableCell key="date" className="font-mono text-xs">
                    {formatDate(match.fixtureStart)}
                  </TableCell>
                  <TableCell key="home">
                    <div className="flex items-center gap-2">
                      <Avatar className="h-6 w-6">
                        <AvatarImage 
                          src={match.raw_data?.homeParticipantLogo ? 
                            `https://www.h2hggl.com/assets/${match.raw_data.homeParticipantLogo}` : 
                            undefined
                          } 
                          alt={match.homePlayer.name} 
                        />
                        <AvatarFallback className="text-xs">
                          {match.homePlayer.name.substring(0, 2)}
                        </AvatarFallback>
                      </Avatar>
                      <span className="font-medium">{match.homePlayer.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Avatar className="h-6 w-6">
                        <AvatarImage 
                          src={match.raw_data?.awayParticipantLogo ? 
                            `https://www.h2hggl.com/assets/${match.raw_data.awayParticipantLogo}` : 
                            undefined
                          } 
                          alt={match.awayPlayer.name} 
                        />
                        <AvatarFallback className="text-xs">
                          {match.awayPlayer.name.substring(0, 2)}
                        </AvatarFallback>
                      </Avatar>
                      <span className="font-medium">{match.awayPlayer.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Badge variant="outline" className="text-xs">
                        {match.homeTeam.name.split(' ').pop()}
                      </Badge>
                      <span className="text-xs text-muted-foreground">vs</span>
                      <Badge variant="outline" className="text-xs">
                        {match.awayTeam.name.split(' ').pop()}
                      </Badge>
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
