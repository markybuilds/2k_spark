import Link from 'next/link'

export function Footer() {
  return (
    <footer className="border-t border-border py-6">
      <div className="container flex flex-col sm:flex-row justify-between items-center">
        <div className="text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} 2K Spark. All rights reserved.
        </div>
        <div className="flex items-center gap-4 mt-4 sm:mt-0">
          <Link href="/about" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            About
          </Link>
          <Link href="/players" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Players
          </Link>
          <Link href="/teams" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Teams
          </Link>
          <span className="text-sm text-muted-foreground">
            Powered by H2H GG League data
          </span>
        </div>
      </div>
    </footer>
  )
}
