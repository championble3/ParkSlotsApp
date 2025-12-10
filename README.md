# ParkingSlotsApp – Instrukcja uruchomienia projektu

**ParkingSlotsApp** to prototypowy system rekomendacji miejsc parkingowych na kampusie Politechniki Wrocławskiej.

System składa się z:
- **Frontend:** React + TypeScript
- **Backend:** Python 3.10.7 + FastAPI
- **Baza danych:** Microsoft SQL Server

---

##  1. Wymagania wstępne

Przed przystąpieniem do instalacji upewnij się, że posiadasz:

*   **Node.js** (zalecana wersja LTS) oraz **npm**.
*   **Python 3.10.7** (wersja wymagana ze względu na kompatybilność bibliotek ML).
*   **Microsoft SQL Server** (lokalna instancja lub dostęp do serwera).
*   **SSMS** (SQL Server Management Studio) do zarządzania bazą.
*   Dostęp do Internetu (pobieranie pakietów, API OpenRouteService, API PWr).
*   Założenie konta na platformie OpenRouteService wraz z utworzeniem klucza API - OPENROUTESERVICE_API_KEY=twoj_klucz_api

---

##  2. Klonowanie repozytorium

Otwórz terminal i wykonaj komendy:

```bash
git clone https://github.com/championble3/ParkSlotsApp.git
cd ParkingSlotsApp
```

---

##  3. Backend – Instalacja i konfiguracja

### 3.1. Przygotowanie środowiska Python

1. Przejdź do katalogu backendu:
   ```bash
   cd backend
   ```

2. Utwórz środowisko wirtualne:
   ```bash
   python -m venv venv
   ```

3. Aktywuj środowisko:
   *   **Windows (PowerShell):**
       ```powershell
       .\venv\Scripts\activate
       ```
   *   **Linux/macOS/Git Bash:**
       ```bash
       source venv/bin/activate
       ```

4. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```

### 3.2. Konfiguracja zmiennych środowiskowych (.env)

W katalogu `backend` utwórz plik o nazwie `.env`. Jest on niezbędny do połączenia z bazą danych i zewnętrznymi API.
Wklej do niego poniższą zawartość, uzupełniając swoje dane:

```env
# --- Konfiguracja Bazy Danych MSSQL ---
DB_SERVER=localhost
# Jeśli używasz SQL Express, wpisz: localhost\SQLEXPRESS
DB_NAME=ParkingDB
DB_USER=twoj_uzytkownik_sql
DB_PASSWORD=twoje_haslo_sql
DB_DRIVER=ODBC Driver 17 for SQL Server

# --- Zewnętrzne API ---
# Klucz do OpenRouteService (wymagany do wyznaczania tras)
OPENROUTESERVICE_API_KEY=twoj_klucz_api
# Klucz do API PWr (opcjonalny, jeśli wymagany przez moduł)
PWR_API_KEY=twoj_klucz_api
```

---

##  4. Frontend – Instalacja i aktualizacja

Otwórz **nowy terminal** i wykonaj następujące kroki:

1. Przejdź do katalogu frontendu:
   ```bash
   cd frontend
   ```

2. Zainstaluj zależności:
   ```bash
   npm install
   ```

3. **(Opcjonalnie)** Aktualizacja pakietów przed deploymentem:
   Zaleca się sprawdzenie i aktualizację bibliotek pod kątem bezpieczeństwa.

   ```bash
   # Sprawdzenie przestarzałych pakietów
   npm outdated

   # Aktualizacja pakietów
   npm update

   # Naprawa znanych luk bezpieczeństwa
   npm audit fix
   ```

---

##  5. Konfiguracja Bazy Danych

1. Uruchom **SQL Server Management Studio (SSMS)**.
2. Utwórz nową bazę danych (np. o nazwie `ParkingDB` – zgodnej z plikiem `.env`).
3. Otwórz nowe okno zapytania (**New Query**) i wykonaj poniższe skrypty.

### 5.1. Tworzenie tabel (Schema)

```sql
-- Tabela budynków
CREATE TABLE buildings (
    building_id INT PRIMARY KEY,
    building_lat FLOAT NOT NULL,
    building_lng FLOAT NOT NULL,
    building_name NVARCHAR(100) NOT NULL
);

-- Tabela parkingów
CREATE TABLE park_info (
    park_id VARCHAR(50) PRIMARY KEY,
    park_lat FLOAT NOT NULL,
    park_lng FLOAT NOT NULL,
    park_name NVARCHAR(100) NOT NULL,
    park_total INT NOT NULL
);

-- Tabela logów jest jedynie potrzebna do dotrenowania modelu predykcyjnego


### 5.2. Wprowadzenie danych początkowych


INSERT INTO buildings (building_id, building_lat, building_lng, building_name) VALUES
(1, 17.059935173378946, 51.108971691869470, 'C3'),
(2, 17.058159406252720, 51.110165633365650, 'D1'),
(3, 17.056716978549960, 51.109870939812580, 'D2'),
(4, 17.058881521224980, 51.107749090758510, 'C13'),
(5, 17.059922218322757, 51.108069058361040, 'C6'),
(6, 17.062540054321293, 51.107737302436110, 'A1'),
(7, 17.059353033415630, 51.109517305068470, 'C16');

INSERT INTO park_info (park_id, park_lat, park_lng, park_name, park_total) VALUES
('park_4', 17.055654816841173, 51.108964955863804, 'Parking Wrońskiego', 207),
('park_2', 17.058339715003970, 51.107528480226634, 'Polinka', 54),
('park_5', 17.059044043772957, 51.109961874023700, 'D20 - D21', 76),
('park_6', 17.055463608139940, 51.104310141218306, 'GEO LO1 Geocentrum', 301),
('park_7', 17.055233253014126, 51.118737867338450, 'Architektura', 79);
```

---

##  6. Uruchomienie Serwerów

### 6.1. Start backendu
W terminalu z aktywnym środowiskiem wirtualnym (katalog `backend`):

```bash
uvicorn app.main:app --reload
```
*   API dostępne pod adresem: `http://127.0.0.1:8000`
*   Dokumentacja Swagger: `http://127.0.0.1:8000/docs`

### 6.2. Start frontendu
W terminalu frontendu (katalog `frontend`):

```bash
npm start
```
Aplikacja powinna automatycznie otworzyć się w przeglądarce pod adresem `http://localhost:3000`.

---

##  Rozwiązywanie problemów (Troubleshooting)

| Problem | Możliwe rozwiązanie |
| :--- | :--- |
| **Błąd połączenia z bazą SQL** | 1. Sprawdź poprawność danych w pliku `.env`.<br>2. Upewnij się, że w *SQL Server Configuration Manager* włączony jest protokół TCP/IP.<br>3. Sprawdź, czy usługa SQL Server Browser działa. |
| **Błąd `Module not found` (Python)** | Upewnij się, że wykonałeś `source venv/bin/activate` lub `.\venv\Scripts\activate` przed instalacją pakietów. |
| **OpenRouteService Error** | Sprawdź, czy klucz API w pliku `.env` jest poprawny i czy posiadasz połączenie z Internetem. |

---

##  Kontakt

W razie problemów z uruchomieniem projektu, proszę o kontakt:
**Email:** 272405@student.pwr.edu.pl

