"use client"

import { useState } from 'react'
import Link from 'next/link'
import { Button } from "@/components/ui/button"
import { refreshData } from "@/lib/api"
import { ReloadIcon } from "@radix-ui/react-icons"
import { MainNav } from "@/components/main-nav"

export function Header() {
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [refreshMessage, setRefreshMessage] = useState<string | null>(null)

  const handleRefresh = async () => {
    setIsRefreshing(true)
    setRefreshMessage(null)

    try {
      const result = await refreshData()
      setRefreshMessage(result.message)
    } catch (error) {
      setRefreshMessage('Failed to refresh data')
    } finally {
      setIsRefreshing(false)

      // Clear message after 3 seconds
      setTimeout(() => {
        setRefreshMessage(null)
      }, 3000)
    }
  }

  return (
    <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
      <div className="container flex h-16 items-center justify-between py-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight">2K Spark</h1>
            <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">Beta</span>
          </Link>

          <MainNav />
        </div>

        <div className="flex items-center gap-4">
          {refreshMessage && (
            <span className={`text-sm ${refreshMessage.includes('Failed') ? 'text-destructive' : 'text-primary'}`}>
              {refreshMessage}
            </span>
          )}

          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            {isRefreshing ? (
              <>
                <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
                Refreshing...
              </>
            ) : (
              <>
                <ReloadIcon className="mr-2 h-4 w-4" />
                Refresh Data
              </>
            )}
          </Button>
        </div>
      </div>
    </header>
  )
}
