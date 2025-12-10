import React, { useState, useEffect } from "react";
import { MapPin, Navigation, Car, Loader2, ExternalLink } from "lucide-react";

interface RecommendationDisplayProps {
  park: string | null;
  isLoading: boolean;
  userLat?: number;
  userLng?: number;
}

function RecommendationDisplay({ park, isLoading, userLat, userLng }: RecommendationDisplayProps) {
  const [location, setLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [loadingLocation, setLoadingLocation] = useState(false);

  useEffect(() => {
    if (!park) return;

    // kontroler do anulowania fetch, jeśli park zmieni się zanim zapytanie się zakończy
    const controller = new AbortController();
    const signal = controller.signal;

    const fetchLocation = async () => {
      setLoadingLocation(true);
      setLocation(null); 
      
      try {
        const res = await fetch(`http://127.0.0.1:8000/map_location?park_name=${encodeURIComponent(park)}`, {
          signal: signal 
        });
        
        if (!res.ok) throw new Error("Nie znaleziono parkingu");
        
        const data = await res.json();
        
        if (!signal.aborted) {
          setLocation(data);
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error("Błąd podczas pobierania lokalizacji:", err);
        }
      } finally {
        if (!signal.aborted) {
          setLoadingLocation(false);
        }
      }
    };

    fetchLocation();

    return () => {
      controller.abort();
    };
  }, [park]); 

  const openGoogleMaps = () => {
    if (!location) return;
    const mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${location.lat},${location.lng}`;
    window.open(mapsUrl, "_blank");
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
        <div className="flex flex-col items-center justify-center text-center">
          <div className="relative mb-6">
            <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
              <Navigation className="w-8 h-8 text-blue-600 animate-pulse" />
            </div>
            <div className="absolute -top-1 -right-1 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
              <Loader2 className="w-3 h-3 text-white animate-spin" />
            </div>
          </div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">Szukam najlepszego parkingu</h3>
          <p className="text-gray-600">Analizuję dostępność miejsc i Twoją lokalizację...</p>
        </div>
      </div>
    );
  }

  if (!park) {
    return null;
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden transition-all duration-300">
      <div className="p-6 bg-gradient-to-r from-green-500 to-emerald-600 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Car className="w-6 h-6" />
          <h2 className="text-xl font-bold">Rekomendacja parkingu</h2>
        </div>
        <p className="text-green-100 text-sm">Znaleziono najlepszy parking dla Ciebie</p>
      </div>

      <div className="p-6">
        {/* seekcja z nazwą parkingu */}
        <div className="flex items-center justify-center p-8 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200 mb-6">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
              <MapPin className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-green-800 mb-2 animate-in fade-in zoom-in duration-300">
              {park}
            </h3>
            <p className="text-green-600">Udaj się do tego parkingu</p>
          </div>
        </div>

        {/* sekcja z przyciskiem */}
        <div className="flex flex-col items-center gap-3">
          <button
            onClick={openGoogleMaps}
            disabled={!location || loadingLocation}
            className={`inline-flex items-center gap-3 px-6 py-3 rounded-xl font-medium transition-all shadow-lg hover:shadow-xl w-full sm:w-auto justify-center
              ${
                location && !loadingLocation
                  ? "bg-blue-600 hover:bg-blue-700 text-white transform hover:-translate-y-0.5"
                  : "bg-gray-100 text-gray-400 cursor-not-allowed border border-gray-200"
              }`}
          >
            {loadingLocation ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Pobieranie współrzędnych...</span>
              </>
            ) : (
              <>
                <MapPin className="w-5 h-5" />
                <span>Zobacz na mapie</span>
                <ExternalLink className="w-4 h-4" />
              </>
            )}
          </button>

          {/* info pomocnicze */}
          {loadingLocation && (
            <p className="text-xs text-gray-400 animate-pulse">Aktualizuję lokalizację dla nowego parkingu...</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default RecommendationDisplay;