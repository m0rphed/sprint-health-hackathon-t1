import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ChartBar, GitBranch } from 'lucide-react';
// import { ChartBar } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex justify-center mb-8">
            <ChartBar className="h-16 w-16 text-primary" />
          </div>
          <h1 className="text-5xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/60">
            Sprint Analysis Dashboard
          </h1>
          <p className="text-xl text-muted-foreground mb-12">
            Upload your sprint data and get instant insights into your team's
            performance. Track velocity, burndown charts, and more with our
            powerful analytics tools.
          </p>

          <div className="space-y-4 md:space-y-0 md:space-x-4">
            <Button asChild size="lg" className="px-8">
              <Link href="/login">Get Started</Link>
            </Button>
            <Button asChild variant="outline" size="lg" className="px-8">
              <Link href="/login?mode=guest">Try as Guest</Link>
            </Button>
          </div>

          <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-card p-6 rounded-lg shadow-lg">
              <div className="h-12 w-12 bg-primary/10 rounded-full flex items-center justify-center mb-4 mx-auto">
                <ChartBar className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">
                Real-time Analytics
              </h3>
              <p className="text-muted-foreground">
                Get instant insights into your sprint performance with
                interactive charts and metrics.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg shadow-lg">
              <div className="h-12 w-12 bg-primary/10 rounded-full flex items-center justify-center mb-4 mx-auto">
                <GitBranch className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Version Control</h3>
              <p className="text-muted-foreground">
                Track changes across sprints and compare performance over time.
              </p>
            </div>

            <div className="bg-card p-6 rounded-lg shadow-lg">
              <div className="h-12 w-12 bg-primary/10 rounded-full flex items-center justify-center mb-4 mx-auto">
                <svg
                  className="h-6 w-6 text-primary"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2">Sprint Planning</h3>
              <p className="text-muted-foreground">
                Use historical data to make informed decisions for future sprint
                planning.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
