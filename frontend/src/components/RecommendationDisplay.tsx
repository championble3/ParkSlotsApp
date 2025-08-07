// RecommendationDisplay.tsx
import React from "react";

interface RecommendationDisplayProps {
  park: string;
}

function RecommendationDisplay({ park }: RecommendationDisplayProps) {
  return <div>Rekomendowany parking: <strong>{park}</strong></div>;
}

export default RecommendationDisplay;
