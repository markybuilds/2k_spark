"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Header } from "@/components/header"
import { Footer } from "@/components/footer"

export default function AboutPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 container py-6 space-y-6">
        <h2 className="text-3xl font-bold tracking-tight">About 2K Spark</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Our Mission</CardTitle>
                <CardDescription>
                  Bringing data-driven insights to basketball gaming
                </CardDescription>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>
                  2K Spark is a cutting-edge platform designed to provide accurate predictions and deep analytics for basketball matches in the H2H GG League. Our mission is to leverage advanced machine learning algorithms and comprehensive historical data to give users valuable insights into upcoming matches.
                </p>
                <p>
                  Whether you're a casual fan looking to enhance your viewing experience or a dedicated enthusiast seeking to understand the game at a deeper level, 2K Spark offers the tools and information you need to stay ahead of the competition.
                </p>
                <p>
                  Our team of data scientists and basketball enthusiasts work tirelessly to improve our prediction models and expand our analytics capabilities, ensuring that 2K Spark remains at the forefront of basketball prediction technology.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>How It Works</CardTitle>
                <CardDescription>
                  The science behind our predictions
                </CardDescription>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>
                  2K Spark uses a sophisticated machine learning pipeline to generate predictions for upcoming basketball matches. Here's a simplified overview of our process:
                </p>
                <ol>
                  <li>
                    <strong>Data Collection:</strong> We continuously gather data from the H2H GG League, including match results, player statistics, team performance metrics, and more.
                  </li>
                  <li>
                    <strong>Feature Engineering:</strong> Our system transforms raw data into meaningful features that capture the essence of player and team performance, accounting for factors like recent form, head-to-head records, and playing style.
                  </li>
                  <li>
                    <strong>Model Training:</strong> We employ ensemble machine learning models, combining the strengths of various algorithms to achieve the highest possible prediction accuracy.
                  </li>
                  <li>
                    <strong>Prediction Generation:</strong> For each upcoming match, our system analyzes the relevant data and generates predictions for the winner, score, and confidence level.
                  </li>
                  <li>
                    <strong>Continuous Improvement:</strong> After each match, we evaluate our predictions against the actual results and use this feedback to refine our models, ensuring they become more accurate over time.
                  </li>
                </ol>
                <p>
                  Our current model achieves an accuracy rate of approximately 65% for winner predictions and an average error of ±5 points for score predictions, making it one of the most reliable systems in the industry.
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Key Features</CardTitle>
                <CardDescription>
                  What makes 2K Spark special
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>Real-time match predictions with confidence scores</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>Detailed player statistics and performance metrics</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>Team analysis and historical performance data</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>Head-to-head comparison tools</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>Regular data updates from the H2H GG League</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>User-friendly interface with dark mode by default</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>Responsive design for desktop and mobile devices</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Data Sources</CardTitle>
                <CardDescription>
                  Where we get our information
                </CardDescription>
              </CardHeader>
              <CardContent className="prose dark:prose-invert max-w-none">
                <p>
                  2K Spark relies on high-quality data from the following sources:
                </p>
                <ul>
                  <li>H2H GG League official API</li>
                  <li>Historical match records</li>
                  <li>Player performance statistics</li>
                  <li>Team composition and strategy data</li>
                </ul>
                <p>
                  We update our database regularly to ensure that all predictions and analyses are based on the most current information available.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Contact Us</CardTitle>
                <CardDescription>
                  Get in touch with our team
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">
                  Have questions, feedback, or suggestions? We'd love to hear from you!
                </p>
                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">Email:</span>
                    <span>support@2kspark.com</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">Twitter:</span>
                    <span>@2KSparkPredictions</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">Discord:</span>
                    <span>discord.gg/2kspark</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
