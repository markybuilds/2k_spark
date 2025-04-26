import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import { StatsOverview } from "@/components/stats-overview";
import { UpcomingMatches } from "@/components/upcoming-matches";
import { Predictions } from "@/components/predictions";
import { PlayerStats } from "@/components/player-stats";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 container py-6 space-y-6">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>

        <StatsOverview />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <UpcomingMatches />
          <Predictions />
        </div>

        <PlayerStats />
      </main>

      <Footer />
    </div>
  );
}
