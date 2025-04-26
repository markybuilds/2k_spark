/**
 * Live page for displaying live matches with predictions.
 */

import { LiveMatchList } from "@/components/live/live-match-list";
import { ContentLayout, PageHeader } from "@/components/layout/content-layout";

export const metadata = {
  title: "Live Matches - 2K Flash",
  description: "Live NBA 2K25 eSports matches with predictions",
};

export default function LivePage() {
  return (
    <ContentLayout>
      <PageHeader
        title="Live Matches"
        description="View live NBA 2K25 eSports matches with real-time predictions for live betting."
      />

      <LiveMatchList />
    </ContentLayout>
  );
}
