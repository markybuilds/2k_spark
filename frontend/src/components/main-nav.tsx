"use client"

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { 
  HomeIcon, 
  PersonIcon, 
  LayersIcon, 
  MixerHorizontalIcon,
  InfoCircledIcon,
  HamburgerMenuIcon
} from "@radix-ui/react-icons"

const navItems = [
  {
    name: 'Dashboard',
    href: '/',
    icon: <HomeIcon className="h-4 w-4 mr-2" />
  },
  {
    name: 'Players',
    href: '/players',
    icon: <PersonIcon className="h-4 w-4 mr-2" />
  },
  {
    name: 'Teams',
    href: '/teams',
    icon: <LayersIcon className="h-4 w-4 mr-2" />
  },
  {
    name: 'Compare',
    href: '/compare',
    icon: <MixerHorizontalIcon className="h-4 w-4 mr-2" />
  },
  {
    name: 'About',
    href: '/about',
    icon: <InfoCircledIcon className="h-4 w-4 mr-2" />
  }
]

export function MainNav() {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)
  
  return (
    <div className="flex items-center">
      <div className="hidden md:flex items-center gap-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`px-3 py-2 text-sm font-medium rounded-md flex items-center transition-colors ${
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              }`}
            >
              {item.icon}
              {item.name}
            </Link>
          )
        })}
      </div>
      
      <div className="md:hidden">
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon">
              <HamburgerMenuIcon className="h-5 w-5" />
              <span className="sr-only">Toggle menu</span>
            </Button>
          </SheetTrigger>
          <SheetContent side="left">
            <div className="py-4">
              <h2 className="text-lg font-bold mb-4">2K Spark</h2>
              <nav className="flex flex-col gap-2">
                {navItems.map((item) => {
                  const isActive = pathname === item.href
                  
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setOpen(false)}
                      className={`px-3 py-2 text-sm font-medium rounded-md flex items-center transition-colors ${
                        isActive
                          ? 'bg-primary/10 text-primary'
                          : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                      }`}
                    >
                      {item.icon}
                      {item.name}
                    </Link>
                  )
                })}
              </nav>
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </div>
  )
}
