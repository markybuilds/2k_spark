/**
 * Predictions page for displaying match predictions.
 */

"use client";

import { PredictionList } from "@/components/predictions/prediction-list";
import { ContentLayout, PageHeader } from "@/components/layout/content-layout";

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
