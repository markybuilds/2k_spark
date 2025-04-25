/**
 * Matches page for displaying upcoming matches.
 */

import { MatchList } from "@/components/matches/match-list";
import { ContentLayout, PageHeader } from "@/components/layout/content-layout";

export const metadata = {
  title: "Upcoming Matches - 2K Flash",
  description: "Upcoming NBA 2K25 eSports matches",
};

export default function MatchesPage() {
  return (
    <ContentLayout>
      <PageHeader
        title="Upcoming Matches"
        description="View upcoming NBA 2K25 eSports matches."
      />

      <MatchList />
    </ContentLayout>
  );
}
