# Journie Progress Log

## Status: Day 7 of 8 (Phase 5 Complete)

### Done
- **Backend Skeleton & MongoDB Setup** (Day 1-2)
- **Persistent Chat Memory & Auth** (Day 3-4): Signup, Login, protected routing, and `/chat` persistence.
- **Booking Flow** (Day 4): Seeding, booking creation/viewing, passport expiry, and check-in/check-out date validations.
- **Feature 1 — Document Risk Monitor (Phase 2)** (Day 6):
  - Backend: Deterministic passport validity check vs destination minimum validity regulations for 15+ countries, dynamic visa rule mapping, and dynamic LLM phrasing with database persistence in `document_checks` collection.
  - Frontend: Implemented full Document Risk Monitor checklist details list page in `Documents.jsx` and live status indicators in `Dashboard.jsx` booking cards.
  - Audited and verified 100% complete and working.
- **Feature 2 — Group Trip Consensus Planner** (Day 5):
  - Backend MongoDB collection (`group_trips`) and API routes.
  - Consensus algorithm that filters options satisfying *all* members' budgets, scores them based on overlap with individual preference tags, and ranks them.
  - Groq LLM integration to generate a cohesive "Why this works" explanation based on the scored data (with robust fallback on external service failure).
  - React/Tailwind frontend layout featuring an interactive form to add/remove travelers, input budgets/preferences, view recommended hotel cards with price/per-person cost splits, and browse past plans history.
  - Adhered to strict UI design requirements (zero emojis, MakeMyTrip/Booking.com professional travel layout, real high-quality photo URLs).
- **Phase 3 — Fix Chat UI (Floating Chat Widget)** (Day 7):
  - Transitioned the page-based AI Assistant page to a global floating circular action button fixed bottom-right (`fixed bottom-6 right-6`).
  - Implemented the chat drawer interface that opens/closes as an overlay over any page.
  - Configured state-preservation: by mounting the component globally in `App.jsx` outside `<Routes>`, the chat state remains active while switching pages.
  - Enforced authentication checks so the button is completely hidden on unauthenticated routes (`/login` and `/signup`).
  - Removed dedicated sidebar navigation link and deleted `ChatWindow.jsx`.
- **Phase 4 — Feature 3: In-Trip Live Assistant** (Day 7):
  - Backend: Extended `/chat/` route and `ChatRequest` to accept an optional `booking_id`. Queries the active booking and constructs a grounded LLM system context with destination, dates, and hotel information to guide assistant replies on luggage, transport, delays, and emergencies.
  - Frontend: Added a trip context dropdown within the global `FloatingChatWidget`. Displays the user's active bookings, sending the selected `booking_id` with message requests.
- **Phase 5 — Delete/Cancel for Bookings and Group Trips** (Day 7):
  - Backend: Added protected `DELETE /bookings/{booking_id}` and `DELETE /group-trips/{trip_id}` routes. Implemented soft-delete by setting status to `"cancelled"` in MongoDB, and cleaned up associated `document_checks` entries for cancelled bookings. Added status query parameters to GET routes with fallback support for legacy documents.
  - Frontend:
    - Dashboard: Added "Show cancelled trips" filter checkbox. Implemented cancellation triggers on active booking cards with browser confirmation dialogs, showing red "Cancelled" badges on soft-deleted bookings.
    - Group Planner: Added "Show cancelled" checkbox in the history sidebar list. Appended a cancellation trash button to past plans list items, displaying red "Cancelled" badges on cancelled plans.
---

## Technical Details: Feature 2 (Consensus Planner)

### Backend Components
1. **Schema** (`backend/app/schemas/group_trip_schema.py`):
   - `GroupMemberInput`: `name` (str), `budget` (float), `preferences` (List[str]).
   - `GroupTripCreate`: `trip_name`, `destination`, `num_nights`, `members` (list).
   - `RecommendedHotelOption`: Details of the hotel, per-person split cost, total cost, tag matching score, and dictionary of individual matching tags.
   - `GroupTripResponse`: Standard response wrapping the saved trip document including the generated LLM reasoning.
2. **Routes** (`backend/app/routes/group_trip_routes.py`):
   - `POST /group-trips/`: Saves a new consensus plan.
   - `GET /group-trips/`: Returns user's history of consensus trips.
   - `GET /group-trips/{trip_id}`: Retrieves trip details.
3. **Service** (`backend/app/services/group_trip_service.py`):
   - Filters hotels in destination where `(price_per_night * num_nights) / num_members <= member.budget` for all members.
   - Scores each hotel by summing the number of matching preferences across all members.
   - Sorts hotels by score (descending), then rating (descending), then price per night (ascending).
   - Prompts Groq llama-3.3-70b-versatile to summarize why options work without any emojis.

### Frontend Components
1. **Sidebar Link** (`frontend/src/components/AppLayout.jsx`):
   - Added `Consensus Planner` navigation tab.
2. **Page View** (`frontend/src/pages/GroupPlanner.jsx`):
   - Renders a multi-member interactive form with dynamic preferences selector.
   - Renders hotel detail cards with Unsplash photography, price breakdowns, and visual indicators of which traveler's preferences matched.
   - Includes history sidebar supporting instant load back of prior plans.

---

## How to Test

### 1. Seeding Mock Data
Ensure mock hotel options are populated in MongoDB:
```cmd
cd backend
venv\Scripts\python.exe scripts\seed_hotels.py
```

### 2. Running Automated Tests
Run the automated test scripts to verify API routes, mathematical scoring, sorting, database persistence, and deletion/soft-deletion status flows:
```cmd
cd backend
venv\Scripts\python.exe scripts\test_group_planner.py
venv\Scripts\python.exe scripts\test_bookings.py
venv\Scripts\python.exe scripts\test_deletion_and_status.py
```

### 3. Running Locally
Start both backend and frontend servers:

- **Backend**:
  ```cmd
  cd backend
  venv\Scripts\activate
  uvicorn app.main:app --reload
  ```
- **Frontend**:
  ```cmd
  cd frontend
  npm run dev
  ```

### 4. Manual Testing Walkthrough
1. Access the web app at `http://localhost:5173/` and sign up or log in.
2. Click **Consensus Planner** in the sidebar.
3. Enter a trip name (e.g. "Paris Friends Weekend"), choose destination **Paris**, and set nights to **3**.
4. Configure 3 travelers:
   - **Traveler 1**: Name: Alice, Budget: $1000, Preferences: "luxury", "spa"
   - **Traveler 2**: Name: Bob, Budget: $200, Preferences: "wifi", "budget"
   - **Traveler 3**: Name: Charlie, Budget: $150, Preferences: "wifi", "near-transit"
5. Click **Calculate Consensus Trip**.
6. Verify the recommended options display "Generator Paris Hostel" since it splits to $55.0/person and fits all budgets. Verify details show how Bob's and Charlie's preferences matched and that the AI consensus reason is rendered correctly.
