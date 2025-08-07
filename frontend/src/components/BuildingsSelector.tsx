// src/components/BuildingsSelector.tsx
import React, { useState, useEffect } from "react";
import '../App.css'; 

type BuildingName = string;

interface BuildingsSelectorProps {
  onSelected: (start: BuildingName, end: BuildingName) => void;
}

function BuildingsSelector({ onSelected }: BuildingsSelectorProps) {
  const [buildings, setBuildings] = useState<BuildingName[]>([]);
  const [startBuilding, setStartBuilding] = useState<BuildingName | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/building_names")
      .then(res => {
        if (!res.ok) throw new Error("Błąd sieci lub serwera");
        return res.json();
      })
      .then(data => {
        if (data && Array.isArray(data.building_names)) {
          setBuildings(data.building_names);
        } else {
          console.error("Otrzymano nieprawidłowy format danych:", data);
          setBuildings([]);
        }
      })
      .catch(err => {
        console.error("Błąd podczas pobierania budynków:", err);
        setBuildings([]); 
      });
  }, []); 

  const handleSelect = (name: BuildingName) => {
    if (!startBuilding) {
      setStartBuilding(name);
    } 
    else if (startBuilding !== name) {
      onSelected(startBuilding, name);
      setStartBuilding(null);
    }
  };
  
  const selectionPrompt = !startBuilding ? "startowy" : "końcowy";

  return (
    <div className="container">
      <h1>Wybierz budynek {selectionPrompt}</h1>
      {buildings.length === 0 ? (
        <p>Ładowanie budynków...</p>
      ) : (
        <ul>
          {buildings.map((name) => {
            const isSelected = name === startBuilding;
            const className = `building-item ${isSelected ? "selected" : ""}`;

            return (
              <li
                key={name}
                className={className}
                onClick={() => handleSelect(name)}
              >
                {name}
              </li>
            );
          })}
        </ul>
      )}
      {startBuilding && (
        <div className="selection-info">
          Wybrano budynek startowy: <strong>{startBuilding}</strong>
        </div>
      )}
    </div>
  );
}

export default BuildingsSelector;