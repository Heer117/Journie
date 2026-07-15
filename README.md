# Journie — AI Travel Booking Assistant

Journie is a premium, AI-powered travel booking assistant designed to streamline group travel consensus planning, monitor destination document requirements, and provide real-time, context-grounded travel assistance.

The application adheres to a clean, professional travel-industry aesthetic (inspired by Booking.com and MakeMyTrip), featuring real travel photography, detailed status cards, and a robust emoji-free interface.

---

## Technical Stack

### Backend
* **Runtime:** Python 3.12
* **Framework:** FastAPI
* **Database:** MongoDB Atlas (via Motor async driver)
* **LLM Engine:** Groq API (`llama-3.3-70b-versatile`)
* **Security:** JWT authentication (`python-jose` + `passlib` / `bcrypt`)

### Frontend
* **Build tool:** Vite (React)
* **Styling:** Tailwind CSS (v4) with Custom Vanilla CSS extensions
* **Routing:** `react-router-dom`
* **HTTP Client:** `axios`
* **Icons:** `lucide-react` (Strictly zero emojis used in the UI)

---

## Getting Started

### Prerequisites
* Python 3.12+
* Node.js (v18+)
* MongoDB Atlas cluster or a running local MongoDB instance
* Groq API Key (for consensus explanation and AI assistant)

---

### Backend Setup

1. **Navigate to the backend directory and set up a Python virtual environment:**
   ```cmd
   cd backend
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the `/backend` directory matching the following structure:
   ```env
   MONGODB_URL=mongodb+server://...
   DATABASE_NAME=journie_db
   SECRET_KEY=your_jwt_signing_secret_here
   GROQ_API_KEY=gsk_...
   ```

4. **Seed Mock Hotel Data:**
   Populate MongoDB with the hotel directory used by the consensus and search algorithms:
   ```cmd
   python scripts/seed_hotels.py
   ```

5. **Run the Backend Server:**
   ```cmd
   uvicorn app.main:app --reload --reload-dir app
   ```
   The backend API will be available at `http://127.0.0.1:8000`.

---

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```cmd
   cd ../frontend
   ```

2. **Install node dependencies:**
   ```cmd
   npm install
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the `/frontend` directory:
   ```env
   VITE_API_URL=http://127.0.0.1:8000
   ```

4. **Start the Frontend Development Server:**
   ```cmd
   npm run dev
   ```
   Open `http://localhost:5173/` in your browser.

---

## Project Structure & Architecture

### Backend Separation of Concerns
* **`app/routes/`**: Handles incoming HTTP requests, route definitions, and dependencies (e.g. JWT user authentication validation).
* **`app/services/`**: Houses core business logic, database queries, mathematical consensus scoring, and third-party LLM integrations.
* **`app/schemas/`**: Defines Pydantic validation shapes for strict request and response contracts.

### Frontend Component Layout
* **`src/context/`**: AuthState and user token synchronization.
* **`src/pages/`**: View routers (Dashboard, Document Checklist, Group Planner, Settings).
* **`src/components/`**: Shared view layouts, protecting routing, and the global floating AI chat widget.
* **`src/api/`**: Client axios wrappers containing authorization interceptors.

---

## Core Features

### 1. Document Risk Monitor
* **What it does:** Deterministically checks passport expiration dates and visa requirements against booking durations.
* **Logic:** Employs rule-based validity mapping against regulations of over 15 destination countries (e.g., 6-month rules). Groq LLM is used strictly for formatting and phrasing output, ensuring reliability.
* **UI:** Highlighted alerts directly in dashboard travel booking cards and detailed explanations on the Documents tab.

### 2. Group Trip Consensus Planner
* **What it does:** Simplifies planning for multi-traveler trips with diverging budgets and interests.
* **Consensus Engine:**
  1. Filters hotels where the per-person split cost fits *everyone's* budget.
  2. Scores matching hotels by aggregating traveler preference tags.
  3. Ranks recommendations and asks Groq to explain the fit.
* **UI:** Multi-member forms, tag selectors, pricing breakdowns, and plan history.

### 3. In-Trip Live Assistant
* **What it does:** Global floating drawer providing context-grounded assistant guidance.
* **Grounding:** Attaches selected active trip contexts (hotel names, check-in dates, destinations) to chat payloads, enabling precise answers for luggage rules, travel delays, and local info.

### 4. Soft Deletions & Status Management
* **What it does:** Allows bookings and group plans to be cancelled rather than permanently wiped. Cancelled entries can be toggled in history feeds with full status indicators.

---

## Testing & Verification

### Running Automated Test Scripts
We have structured test scripts in the backend to verify service algorithms:

```cmd
cd backend
# Test MongoDB connection
venv\Scripts\python.exe scripts\test_mongo_connection.py

# Test Consensus mathematical scoring & ranking
venv\Scripts\python.exe scripts\test_group_planner.py

# Test active status, soft deletions, and document risk service updates
venv\Scripts\python.exe scripts\test_deletion_and_status.py
```
