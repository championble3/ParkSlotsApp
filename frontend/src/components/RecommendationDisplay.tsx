import React from "react";
import { MapPin, Navigation, Car, Loader2 } from "lucide-react";

interface RecommendationDisplayProps {
  park: string | null;
  isLoading: boolean;
}

function RecommendationDisplay({ park, isLoading }: RecommendationDisplayProps) {
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
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      <div className="p-6 bg-gradient-to-r from-green-500 to-emerald-600 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Car className="w-6 h-6" />
          <h2 className="text-xl font-bold">Rekomendacja parkingu</h2>
        </div>
        <p className="text-green-100 text-sm">Znaleziono najlepszy parking dla Ciebie</p>
      </div>
      
      <div className="p-6">
        <div className="flex items-center justify-center p-8 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <MapPin className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-2xl font-bold text-green-800 mb-2">{park}</h3>
            <p className="text-green-600">Udaj się do tego parkingu</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RecommendationDisplay;