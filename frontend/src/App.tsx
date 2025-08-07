// src/App.tsx
import React, { useState } from "react";
import BuildingsSelector from "./components/BuildingsSelector";
import RecommendationDisplay from "./components/RecommendationDisplay";

function App() {
  const [recommendedPark, setRecommendedPark] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSelectedBuildings = async (start: string, end: string) => {
    setIsLoading(true);
    setError(null);
    setRecommendedPark(null); 

    try {
      const currentDateTime = new Date().toISOString();

      const response = await fetch("http://127.0.0.1:8000/recommended_park", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          first_building: start,
          last_building: end,
          date_time: currentDateTime, 
        }),
      });

      if (!response.ok) {
        throw new Error(`Błąd serwera: ${response.statusText}`);
      }

      const data = await response.json();
      setRecommendedPark(data.recommended_park);
    } catch (err: any) {
      console.error("Błąd przy pobieraniu rekomendacji:", err);
      setError("Nie udało się pobrać rekomendacji. Spróbuj ponownie.");
    } finally {
      setIsLoading(false); 
    }
  };

  return (
    <div>
      <BuildingsSelector onSelected={handleSelectedBuildings} />
      
      {isLoading && <p>Szukam rekomendacji...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {recommendedPark && <RecommendationDisplay park={recommendedPark} />}
    </div>
  );
}

export default App;