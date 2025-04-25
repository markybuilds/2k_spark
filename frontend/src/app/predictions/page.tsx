/**
 * Predictions page for displaying match predictions.
 */

import { PredictionList } from "@/components/predictions/prediction-list";
import { ContentLayout, PageHeader } from "@/components/layout/content-layout";

export const metadata = {
  title: "Match Predictions - 2K Flash",
  description: "Predictions for upcoming NBA 2K25 eSports matches",
};

export default function PredictionsPage() {
  return (
    <ContentLayout>
      <PageHeader
        title="Match Predictions"
        description="View predictions for upcoming NBA 2K25 eSports matches."
      />

      <PredictionList />
    </ContentLayout>
  );
}
