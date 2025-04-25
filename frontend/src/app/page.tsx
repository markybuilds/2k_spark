import Link from "next/link";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="space-y-8">
      <div className="text-center py-10 space-y-4">
        <h1 className="text-4xl font-bold">2K Flash</h1>
        <p className="text-xl text-muted-foreground">
          NBA 2K25 eSports Match Prediction System
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <Card>
          <CardHeader>
            <CardTitle>Match Predictions</CardTitle>
            <CardDescription>
              Predictions for upcoming matches
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p>View winner predictions for upcoming NBA 2K25 eSports matches with confidence levels.</p>
          </CardContent>
          <CardFooter>
            <Button asChild>
              <Link href="/predictions">View Predictions</Link>
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Upcoming Matches</CardTitle>
            <CardDescription>
              Schedule of upcoming matches
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p>View the schedule of upcoming NBA 2K25 eSports matches in the H2H GG League.</p>
          </CardContent>
          <CardFooter>
            <Button asChild>
              <Link href="/matches">View Matches</Link>
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Player Statistics</CardTitle>
            <CardDescription>
              Stats for individual players
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p>Explore detailed statistics for NBA 2K25 eSports players in the H2H GG League.</p>
          </CardContent>
          <CardFooter>
            <Button asChild>
              <Link href="/players">View Players</Link>
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Score Predictions</CardTitle>
            <CardDescription>
              Predicted scores for upcoming matches
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p>Get detailed score predictions with point differentials for upcoming matches.</p>
          </CardContent>
          <CardFooter>
            <Button asChild>
              <Link href="/scores">View Scores</Link>
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Prediction History</CardTitle>
            <CardDescription>
              Historical predictions and results
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p>Analyze past predictions and compare with actual results to evaluate accuracy.</p>
          </CardContent>
          <CardFooter>
            <Button asChild>
              <Link href="/history">View History</Link>
            </Button>
          </CardFooter>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistics</CardTitle>
            <CardDescription>
              Prediction statistics and metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p>View overall prediction statistics, model accuracy, and other metrics.</p>
          </CardContent>
          <CardFooter>
            <Button asChild>
              <Link href="/stats">View Stats</Link>
            </Button>
          </CardFooter>
        </Card>
      </div>

      <div className="mt-12 text-center">
        <h2 className="text-2xl font-bold mb-4">About 2K Flash</h2>
        <p className="max-w-3xl mx-auto text-muted-foreground">
          2K Flash is a comprehensive prediction system for NBA 2K25 eSports matches in the H2H GG League.
          The system collects data from the H2H GG League API, processes player statistics, and uses
          machine learning models to predict match winners and scores with high accuracy.
        </p>
      </div>
    </div>
  );
}
