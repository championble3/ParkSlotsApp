import React, { useState, useRef } from "react";
import BuildingsSelector from "./components/BuildingsSelector";
import RecommendationDisplay from "./components/RecommendationDisplay";

function App() {
  const [recommendedPark, setRecommendedPark] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  const handleSelectedBuildings = (start: string, end: string) => {
    setIsLoading(true);
    setError(null);
    setRecommendedPark(null);

    if (socketRef.current) {
      socketRef.current.close();
    }

    const socket = new WebSocket("ws://127.0.0.1:8000/recommended_park");
    socketRef.current = socket;

    let locationInterval: NodeJS.Timeout;

    socket.onopen = () => {
      console.log("Połączono z WebSocket");

      function sendLocation() {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            console.log('Dokładność GPS (m):', position.coords.accuracy);
            const data = {
              first_building: start,
              last_building: end,
              user_lat: position.coords.latitude,
              user_lng: position.coords.longitude,
              date_time: new Date().toISOString(),
            };
            socket.send(JSON.stringify(data));
          },
          (error) => {
            console.error("Błąd geolokalizacji:", error);
          },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
  
        );
      }

      sendLocation();
      locationInterval = setInterval(sendLocation, 1000);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setRecommendedPark(data.recommended_park);
      setIsLoading(false);
    };

    socket.onerror = (err) => {
      console.error("Błąd WebSocket:", err);
      setError("Błąd połączenia z serwerem.");
      setIsLoading(false);
    };

    socket.onclose = () => {
      console.log("Połączenie WebSocket zamknięte");
      if (locationInterval) {
        clearInterval(locationInterval);
      }
    };
  };

  return (
    <div>
      <BuildingsSelector onSelected={handleSelectedBuildings} />
      {isLoading && <p>Szukam rekomendacji...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {recommendedPark && <RecommendationDisplay park={recommendedPark} />}
    </div>
  );
}

export default App;
