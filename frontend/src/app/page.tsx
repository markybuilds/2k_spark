import Link from "next/link";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  BarChart3,
  Calendar,
  Users,
  Calculator,
  History,
  LineChart,
  ArrowRight
} from "lucide-react";

export default function Home() {
  return (
    <div className="space-y-20">
      {/* Hero Section */}
      <div className="relative -mx-6 -mt-10 px-6 py-24 hero-gradient rounded-b-3xl overflow-hidden">
        <div className="absolute inset-0 bg-grid-white [mask-image:linear-gradient(0deg,transparent,rgba(255,255,255,0.8),transparent)]"></div>
        <div className="relative max-w-5xl mx-auto text-center space-y-8">
          <h1 className="text-6xl font-bold tracking-tight text-white">
            <span className="inline-block">2K Flash</span>
          </h1>
          <p className="text-xl text-white/90 max-w-3xl mx-auto leading-relaxed">
            Advanced prediction system for NBA 2K25 eSports matches with machine learning-powered insights
          </p>
          <div className="flex justify-center gap-6 mt-10">
            <Button asChild size="lg" className="gap-2">
              <Link href="/predictions">
                Get Predictions
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="bg-white/10 hover:bg-white/20 text-white border-white/20">
              <Link href="/stats">View Stats</Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="content-layout">
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          <Card className="card-hover">
            <CardHeader className="pb-4">
              <BarChart3 className="h-10 w-10 text-primary mb-3" />
              <CardTitle className="text-xl">Match Predictions</CardTitle>
              <CardDescription className="text-sm mt-1">
                Predictions for upcoming matches
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-base">View winner predictions for upcoming NBA 2K25 eSports matches with confidence levels based on advanced analytics.</p>
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link href="/predictions">View Predictions</Link>
              </Button>
            </CardFooter>
          </Card>

          <Card className="card-hover">
            <CardHeader>
              <Calendar className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Upcoming Matches</CardTitle>
              <CardDescription>
                Schedule of upcoming matches
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>View the schedule of upcoming NBA 2K25 eSports matches in the H2H GG League with detailed information.</p>
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link href="/matches">View Matches</Link>
              </Button>
            </CardFooter>
          </Card>

          <Card className="card-hover">
            <CardHeader>
              <Users className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Player Statistics</CardTitle>
              <CardDescription>
                Stats for individual players
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>Explore detailed statistics for NBA 2K25 eSports players in the H2H GG League with performance metrics.</p>
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link href="/players">View Players</Link>
              </Button>
            </CardFooter>
          </Card>

          <Card className="card-hover">
            <CardHeader>
              <Calculator className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Score Predictions</CardTitle>
              <CardDescription>
                Predicted scores for upcoming matches
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>Get detailed score predictions with point differentials for upcoming matches based on player performance data.</p>
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link href="/scores">View Scores</Link>
              </Button>
            </CardFooter>
          </Card>

          <Card className="card-hover">
            <CardHeader>
              <History className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Prediction History</CardTitle>
              <CardDescription>
                Historical predictions and results
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>Analyze past predictions and compare with actual results to evaluate accuracy and track model performance.</p>
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link href="/history">View History</Link>
              </Button>
            </CardFooter>
          </Card>

          <Card className="card-hover">
            <CardHeader>
              <LineChart className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Statistics</CardTitle>
              <CardDescription>
                Prediction statistics and metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>View overall prediction statistics, model accuracy, and other metrics to understand prediction performance.</p>
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link href="/stats">View Stats</Link>
              </Button>
            </CardFooter>
          </Card>
        </div>
      </div>

      {/* About Section */}
      <div className="content-layout">
        <div className="mt-20 text-center bg-card rounded-xl p-10 border">
          <h2 className="text-3xl font-bold mb-6 gradient-text">About 2K Flash</h2>
          <p className="max-w-3xl mx-auto text-muted-foreground text-lg">
            2K Flash is a comprehensive prediction system for NBA 2K25 eSports matches in the H2H GG League.
            The system collects data from the H2H GG League API, processes player statistics, and uses
            machine learning models to predict match winners and scores with high accuracy.
          </p>
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            <div className="flex flex-col items-center md:items-start">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <span className="text-primary font-bold">1</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Data Collection</h3>
              <p className="text-sm text-muted-foreground">Real-time data from H2H GG League API with player and match statistics</p>
            </div>
            <div className="flex flex-col items-center md:items-start">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <span className="text-primary font-bold">2</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Analysis</h3>
              <p className="text-sm text-muted-foreground">Advanced statistical models process player performance and match history</p>
            </div>
            <div className="flex flex-col items-center md:items-start">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <span className="text-primary font-bold">3</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Predictions</h3>
              <p className="text-sm text-muted-foreground">Machine learning algorithms generate accurate match and score predictions</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
