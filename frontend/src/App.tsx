import React, { useState, useRef } from "react";
import { Navigation, Car, AlertCircle } from "lucide-react";
import BuildingsSelector from "./components/BuildingsSelector";
import RecommendationDisplay from "./components/RecommendationDisplay";

function App() {
  const [recommendedPark, setRecommendedPark] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [locationStatus, setLocationStatus] = useState<"inactive" | "requesting" | "active" | "success" | "error">("inactive");
  const [userLocation, setUserLocation] = useState<{lat: number, lng: number} | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  const handleSelectedBuildings = async (start: string, end: string) => {
    setIsLoading(true);
    setError(null);
    setRecommendedPark(null);
    setLocationStatus("requesting");

    if (!navigator.geolocation) {
      setError("Geolokalizacja nie jest dostępna w tej przeglądarce");
      setIsLoading(false);
      return;
    }

    if (socketRef.current) {
      socketRef.current.close();
    }

    try {
      const socket = new WebSocket("ws://127.0.0.1:8000/recommended_park");
      socketRef.current = socket;

      let locationInterval: NodeJS.Timeout;

      socket.onopen = () => {
        console.log("Connected to WebSocket");
        setLocationStatus("active");

        const sendLocation = () => {
          // Sprawdzamy, czy połączenie jest otwarte przed próbą wysłania
          if (socket.readyState !== WebSocket.OPEN) return;

          navigator.geolocation.getCurrentPosition(
            (position) => {
              const lat = position.coords.latitude;
              const lng = position.coords.longitude;
              
              setUserLocation({ lat, lng });
              
              const data = {
                first_building: start,
                last_building: end,
                user_lat: lat,
                user_lng: lng,
                date_time: new Date().toISOString(), // Aktualizacja czasu przy każdym wysłaniu
              };
              socket.send(JSON.stringify(data));
            },
            (error) => {
              console.error("Geolocation error:", error);
              // Nie przerywamy interwału przy pojedynczym błędzie, tylko logujemy
              setLocationStatus("error");
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
          );
        };

        // Pierwsze wywołanie natychmiast
        sendLocation();
        
        // Kolejne wywołania co 2 minuty (120000 ms)
        locationInterval = setInterval(sendLocation, 120000);
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setRecommendedPark(data.recommended_park);
        setIsLoading(false);
        setLocationStatus("success");
      };

      socket.onerror = (err) => {
        console.error("WebSocket error:", err);
        setError("Błąd połączenia z serwerem. Spróbuj ponownie.");
        setIsLoading(false);
        setLocationStatus("error");
      };

      socket.onclose = () => {
        console.log("WebSocket connection closed");
        if (locationInterval) {
          clearInterval(locationInterval);
        }
        // Jeśli zamknięcie nie było celowe (resetApp), status może pozostać
      };
    } catch (err) {
      setError("Nie udało się nawiązać połączenia");
      setIsLoading(false);
      setLocationStatus("error");
    }
  };

  const resetApp = () => {
    if (socketRef.current) {
      socketRef.current.close();
    }
    setRecommendedPark(null);
    setIsLoading(false);
    setError(null);
    setLocationStatus("inactive");
    setUserLocation(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-white rounded-full px-6 py-3 shadow-lg border border-gray-100 mb-4">
            <Car className="w-5 h-5 text-blue-600" />
            <span className="font-bold text-gray-800">PwrParking</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Inteligentne parkowanie</h1>
          <p className="text-gray-600">Znajdź najlepszy parking w czasie rzeczywistym</p>
        </div>

        {locationStatus !== "inactive" && (
          <div className="mb-6">
            <div className={`
              flex items-center gap-3 p-4 rounded-xl border-2 
              ${locationStatus === "requesting" ? "bg-yellow-50 border-yellow-200 text-yellow-800" : ""}
              ${locationStatus === "active" ? "bg-blue-50 border-blue-200 text-blue-800" : ""}
              ${locationStatus === "success" ? "bg-green-50 border-green-200 text-green-800" : ""}
              ${locationStatus === "error" ? "bg-red-50 border-red-200 text-red-800" : ""}
            `}>
              <Navigation className={`w-5 h-5 ${locationStatus === "active" ? "animate-pulse" : ""}`} />
              <span className="font-medium">
                {locationStatus === "requesting" && "Żądanie dostępu do lokalizacji..."}
                {locationStatus === "active" && "Śledzenie lokalizacji aktywne"}
                {locationStatus === "success" && "Lokalizacja potwierdzona"}
                {locationStatus === "error" && "Błąd lokalizacji"}
              </span>
            </div>
          </div>
        )}

        <div className="space-y-6">
          <BuildingsSelector onSelected={handleSelectedBuildings} />

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <span className="text-red-800 font-medium">{error}</span>
              </div>
            </div>
          )}

          {(isLoading || recommendedPark) && (
            <RecommendationDisplay 
              park={recommendedPark} 
              isLoading={isLoading} 
              userLat={userLocation?.lat}
              userLng={userLocation?.lng}
            />
          )}

          {(isLoading || recommendedPark || error) && (
            <div className="text-center">
              <button
                onClick={resetApp}
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-3 rounded-xl font-medium transition-colors"
              >
                Nowe wyszukiwanie
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;