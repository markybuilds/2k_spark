/**
 * History page for displaying prediction history.
 */

import { HistoryTable } from "@/components/history/history-table";

export const metadata = {
  title: "Prediction History - 2K Flash",
  description: "Historical predictions for NBA 2K25 eSports matches",
};

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Prediction History</h1>
        <p className="text-muted-foreground">
          View historical predictions for NBA 2K25 eSports matches.
        </p>
      </div>
      
      <HistoryTable />
    </div>
  );
}
