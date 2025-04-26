/**
 * History page for displaying prediction history.
 */

import { HistoryTable } from "@/components/history/history-table";
import { ContentLayout, PageHeader } from "@/components/layout/content-layout";

export const metadata = {
  title: "Prediction History - 2K Flash",
  description: "Historical predictions for NBA 2K25 eSports matches",
};

export default function HistoryPage() {
  return (
    <ContentLayout>
      <PageHeader
        title="Prediction History"
        description="View historical predictions for NBA 2K25 eSports matches with filtering options."
      />

      <HistoryTable />
    </ContentLayout>
  );
}
