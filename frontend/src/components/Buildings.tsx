import React, { useState, useEffect } from "react";
import "../App.css"; // lub inna ścieżka do pliku z powyższym CSS

type BuildingName = string;

function BuildingsSelector() {
  const [buildings, setBuildings] = useState<BuildingName[]>([]);
  const [step, setStep] = useState<"start" | "end">("start");
  const [startBuilding, setStartBuilding] = useState<BuildingName | null>(null);
  const [endBuilding, setEndBuilding] = useState<BuildingName | null>(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/buildings")
      .then((res) => res.json())
      .then((data: { buildings: BuildingName[] }) => setBuildings(data.buildings))
      .catch(() => console.error("Error"));
  }, []);

  const handleSelect = (name: BuildingName) => {
    if (step === "start") {
      setStartBuilding(name);
      setStep("end");
    } else if (step === "end") {
      setEndBuilding(name);
      alert(`Start: ${startBuilding}, End: ${name}`);
      // reset
      setStartBuilding(null);
      setEndBuilding(null);
      setStep("start");
    }
  };

  return (
    <div className="container">
      <h1>Wybierz budynek {step === "start" ? "początkowy" : "końcowy"}</h1>
      <ul>
        {buildings.map((name) => {
        const isSelected =
          (step === "start" && name === startBuilding) || 
          (step === "end" && name === endBuilding);      
          return (
            <li
              key={name}
              className={isSelected ? "selected" : ""}
              onClick={() => !isSelected && handleSelect(name)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if ((e.key === "Enter" || e.key === " ") && !isSelected) {
                  handleSelect(name);
                }
              }}
            >
              {name}
            </li>
          );
        })}
      </ul>
      <div className="selection-info">
        {startBuilding && <p>Wybrany budynek startowy: {startBuilding}</p>}
        {endBuilding && <p>Wybrany budynek końcowy: {endBuilding}</p>}
      </div>
    </div>
  );
}

export default BuildingsSelector;
