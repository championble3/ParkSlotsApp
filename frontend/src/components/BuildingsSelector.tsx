import React, { useState, useEffect } from "react";
import { Building2, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

type BuildingName = string;

interface BuildingsSelectorProps {
  onSelected: (start: BuildingName, end: BuildingName) => void;
}

function BuildingsSelector({ onSelected }: BuildingsSelectorProps) {
  const [buildings, setBuildings] = useState<BuildingName[]>([]);
  const [startBuilding, setStartBuilding] = useState<BuildingName | null>(null);
  const [isLoadingBuildings, setIsLoadingBuildings] = useState<boolean>(true);
  const [buildingError, setBuildingError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBuildings = async () => {
      try {
        setIsLoadingBuildings(true);
        const response = await fetch("http://127.0.0.1:8000/building_names");
        if (!response.ok) throw new Error("Failed to fetch buildings");
        
        const data = await response.json();
        if (data && Array.isArray(data.building_names)) {
          setBuildings(data.building_names);
        } else {
          throw new Error("Invalid data format");
        }
      } catch (err) {
        console.error("Error fetching buildings:", err);
        setBuildingError("Nie udało się załadować listy budynków");
        setBuildings([]);
      } finally {
        setIsLoadingBuildings(false);
      }
    };

    fetchBuildings();
  }, []);

  const handleSelect = (name: BuildingName) => {
    if (!startBuilding) {
      setStartBuilding(name);
    } else if (startBuilding !== name) {
      onSelected(startBuilding, name);
      setStartBuilding(null);
    }
  };

  const resetSelection = () => {
    setStartBuilding(null);
  };

  if (isLoadingBuildings) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-4" />
        <p className="text-gray-600">Ładowanie budynków...</p>
      </div>
    );
  }

  if (buildingError) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-white rounded-2xl shadow-lg border border-gray-100">
        <AlertCircle className="w-8 h-8 text-red-500 mb-4" />
        <p className="text-red-600 text-center">{buildingError}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      <div className="p-6 bg-gradient-to-r from-blue-500 to-purple-600 text-white">
        <div className="flex items-center gap-3 mb-2">
          <Building2 className="w-6 h-6" />
          <h1 className="text-xl font-bold">
            {!startBuilding ? "Wybierz budynek startowy" : "Wybierz budynek końcowy"}
          </h1>
        </div>
        <p className="text-blue-100 text-sm">
          {!startBuilding ? "Kliknij budynek, od którego zaczniesz" : "Kliknij budynek, do którego zmierzasz"}
        </p>
      </div>

      {startBuilding && (
        <div className="p-4 bg-green-50 border-b border-green-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-green-800 font-medium">
                Start: <strong>{startBuilding}</strong>
              </span>
            </div>
            <button
              onClick={resetSelection}
              className="text-green-600 hover:text-green-800 text-sm font-medium transition-colors"
            >
              Zmień
            </button>
          </div>
        </div>
      )}

      <div className="p-6">
        <div className="grid gap-3 max-h-96 overflow-y-auto">
          {buildings.map((name) => {
            const isSelected = name === startBuilding;

            return (
              <button
                key={name}
                onClick={() => handleSelect(name)}
                className={`
                  p-4 rounded-xl text-left font-medium transition-all duration-200 transform
                  ${isSelected 
                    ? "bg-green-100 text-green-800 border-2 border-green-300" 
                    : startBuilding 
                      ? "bg-blue-50 text-blue-700 border-2 border-blue-200 hover:bg-blue-100 hover:border-blue-300 hover:scale-[1.02] shadow-sm" 
                      : "bg-gray-50 text-gray-700 border-2 border-gray-200 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 hover:scale-[1.02] shadow-sm"
                  }
                  hover:shadow-md
                `}
              >
                <div className="flex items-center gap-3">
                  <Building2 className="w-4 h-4" />
                  <span>{name}</span>
                  {isSelected && <CheckCircle className="w-4 h-4 text-green-600 ml-auto" />}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default BuildingsSelector;