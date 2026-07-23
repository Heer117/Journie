# Journie Progress Log

## Status: Phase F (AI-ify Group Consensus Planner) Completed

### Phase F: AI-ify Group Consensus Planner (July 24, 2026)
- **Semantic Preference Matching**: Upgraded the group consensus matching in `group_trip_service.py` to leverage the LLM for semantic tag overlaps (e.g. mapping traveler prefers "swimming pool" to hotel's "pool" or "quiet" to "peaceful").
- **Budget Compromise Suggestions**: Implemented safety floor deterministic checks that prevent recommendations breaking hard budget splits, coupled with active LLM compromises (proposing budget adjustments or duration reductions) when no hotels fit everyone's budget.
- **Custom Reasoning Generation**: Direct LLM JSON schema responses generating structured explanations highlighting specific travelers' preference matches.
- **Verification**: Created and executed `scripts/test_phase_f_semantics.py` validating semantic preference mapping and Paris budget compromise. All tests passed.

### Phase E: AI Travel Suggestions During Booking (July 21, 2026)
- **Direct Suggestions Service:** Created `get_booking_suggestions_llm` in `llm_service.py` and `get_booking_suggestions` in `booking_service.py` using direct LLM prompts to synthesize seasonal highlights and recommended activities for any destination and date range.
- **FastAPI Endpoints:** Created a protected `GET /bookings/suggestions` endpoint in `booking_routes.py` resolving traveler authentication and suggestions.
- **Dynamic Suggestions UI Panel:** Updated `Dashboard.jsx` to import `ReactMarkdown`, track destination and date state variables, and debouce a request to the suggestions API on input. Rendered an elegant "AI Suggestions" panel with Lucide icons (`Sparkles`, `Compass`, `CalendarDays`) and loading skeletons.
- **Verification:** Created and executed `scripts/test_suggestions_api.py` validating correct authentication validation and suggestions payloads in ASGI in-memory tests. All tests passed.

### Phase D: Agentic Booking & Cancellation Tools (July 21, 2026)
- **Agentic Booking & Cancellation Tools:** Registered `search_hotels`, `create_booking`, and `cancel_booking` as LangChain `@tool` functions in `llm_service.py`.
- **Conversational Validation & Confirmation:** Updated prompt directives in `chat_routes.py` and tool definitions to conversationally collect required fields (destination, hotel choice, check-in, check-out dates, passport expiry if international) across turns and require user confirmation prior to calling booking/cancellation tools.
- **Server-Side Validation Guardrails:** Reused `booking_service` functions (`create_user_booking` and `delete_user_booking`) within tools so agentic bookings enforce date checks, overlap rules, domestic passport bypasses, and automatic document verification creation.
- **Resilient Tool Execution:** Added regex recovery logic in `run_agent_chat` to catch and parse raw LLM tool call strings (`<function=...></function>`) if Groq returns 400 format exceptions.
- **Verification:** Created and executed `scripts/test_phase_d_agent_tools.py` verifying hotel lookup, booking creation, and soft-cancellation via the conversational agent. All tests passed.

### Phase C: Full Trip Context + Weather Tool + SerpAPI Tool (July 21, 2026)
- **Agent Tools Scaffolded & Registered:** Created `get_user_trips`, `get_weather`, and `search_places` tools as LangChain `@tool` functions in `llm_service.py`.
- **Dynamic User Trip Retrieval (`get_user_trips`):** Replaced manual UI trip-selection dropdown in `FloatingChatWidget.jsx` with an autonomous agent tool. The assistant queries MongoDB dynamically for the user's active/past bookings, passport expiry, and document check statuses whenever requested in conversation.
- **Live Weather Integration (`get_weather`):** Integrated Open-Meteo geocoding and daily forecast API (with fallbacks for out-of-range dates and WMO code descriptions) to retrieve real-time weather forecasts for any destination.
- **Search & Attraction Research (`search_places`):** Integrated SerpAPI with DuckDuckGo fallback for place recommendations, itineraries, and top sights.
- **Verification:** Created and executed `scripts/test_phase_c_agent_tools.py` verifying tool invocation, API queries, and output formatting. All tests passed.

### Phase H: Expand Destination & Hotel Dataset (July 20, 2026)
- **Hotels & Destinations Expansion:** Expanded the dataset in `seed_hotels.py` from 5 to 17 destinations (6 domestic: Goa, Manali, Jaipur, Udaipur, Kerala, Rishikesh; 11 international: Tokyo, Paris, London, Rome, New York, Thailand, Dubai, Singapore, Bali, Switzerland, Maldives), seeding 4 unique hotels per destination (68 hotels total) with realistic pricing, ratings, descriptions, and amenities.
- **Seeding Logic Update:** Changed the database seeding strategy to use `update_one` with `upsert=True` matching name and destination. This adds new hotels and updates existing ones alongside current data without wiping the collection, preserving the `_id` references of existing hotels and preventing bookings from breaking.
- **Domestic Document Bypass:** Implemented a bypass in `document_check_service.py` and `Documents.jsx` for domestic Indian destinations. When booking a domestic trip, passport/visa checks are completely skipped, immediately returning a status of `Ready` with the reason `"This is a domestic trip within India. Passport validity and visa requirements do not apply."`, and updating the UI checklist to reflect that passport expiry, destination validity, and visa checks are not required.
- **Frontend Dropdowns and Image Mapping:** Expanded destination selection dropdowns and mapped high-quality Unsplash image URLs for all 17 destinations across `Dashboard.jsx`, `Documents.jsx`, and `GroupPlanner.jsx`.

### Phase B: Markdown-Formatted Chat Replies (July 20, 2026)

### Phase A: LangChain Foundational Refactor (July 19, 2026)
- **LangChain ChatGroq Integration:** Replaced direct Groq SDK client with LangChain `ChatGroq` wrapper in `llm_service.py`.
- **Memory Serialization Refactor:** Converted MongoDB-based conversation storage to serialize and deserialize messages using LangChain's serialization formats (`message_to_dict` and `messages_from_dict`).
- **Agent Scaffold:** Created a `create_tool_calling_agent` and `AgentExecutor` scaffold in `llm_service.py` with a dynamic prompt template and an empty tool list.
- **Verification:** Successfully ran all `test_live_assistant.py` integration tests verifying correctness of formatting, absence of emojis, and API responses. Verified new message schema structure in MongoDB.

### Phase 1 Audit Findings & Verification (July 17, 2026)
We have completed a full code-level audit of the codebase to verify functionality across the existing booking flow, auth mechanisms, Chat assistant state, consensus planner, and document check system. Below is the detailed verification status and the minor gaps identified:

#### 1. Booking Flow
- **Search & Results:** Verified. Populates hotel selection via `GET /bookings/hotels?destination=...` upon selecting one of the hardcoded destinations in the UI.
- **Create Booking & Validation:** Verified. Enforces that:
  - Check-in date is not in the past (`start_date >= today`).
  - Check-out date is strictly after check-in (`end_date > start_date`).
  - Passport expiry is in the future (`passport_expiry > today`).
  - Date format matches `YYYY-MM-DD`.
  - Validations are enforced in both the frontend form (`Dashboard.jsx`) and the backend Pydantic model (`BookingCreate`) + service layer (`booking_service.py`).
- **Gaps found:**
  - In the frontend (`Dashboard.jsx`), destination selection is restricted to 5 hardcoded cities (Tokyo, Paris, London, Rome, New York) in a dropdown. There is no free-text search for custom destinations, even though the backend supports general text regex matches.
  - Date comparison relies on client-side local timezone `Date` parsing on the frontend vs server-side `datetime.date.today()` on the backend, which may lead to edge-case validation mismatches around midnight.

#### 2. Feature 1 (Document Risk Monitor)
- **Status:** Complete.
- **Verification:** Verified backend logic (`document_check_service.py`) checks minimum passport validity requirement (90 or 180 days) for 15+ countries against return date, generates conversational AI response rephrasing via Groq (without emojis and under 50 words), and falls back to deterministic raw reasoning if the API fails. Frontend (`Documents.jsx`) correctly renders status badges, LLM reasoning block, and the 3-point checklist panel.
- **Gaps found:**
  - The checklist items on the frontend have minor redundancy, where passport future expiration is checked on the client side using `isPassportValid` while the remaining checks rely on the backend.
  - No visual explanation of the exact "days short" is shown on the frontend UI except within the LLM-phrased reason text itself.

#### 3. Feature 2 (Group Consensus Planner)
- **Status:** Complete & Working.
- **Verification:** Scored consensus filters hotels by per-person split budget (`price_per_night * num_nights / num_members <= member.budget` for all members), computes overlapping preferences tag score, ranks recommended options, and prompts Groq LLM to generate a professional travel consensus summary reasoning text.
- **Gaps found:** None. Algorithms, schema verification, and database persistence are fully intact and correct.

#### 4. Auth Enforcement
- **Status:** Verified.
- **Verification:** Frontend protected routes are guarded via `<ProtectedRoute>` component which checks the `isAuthenticated` state from `AuthContext` and redirects to `/login` if not logged in. Backend routes require the `Authorization` header with a valid JWT via `get_current_user` dependency.
- **Gaps found:**
  - The hotel search route `GET /bookings/hotels` is currently public (no `get_current_user` dependency on backend), although in the UI it is nested inside the protected Dashboard route.
  - Unauthenticated routes like `/login` or `/signup` do not auto-redirect authenticated users to `/` if they manually navigate back to them.

#### 5. Chat UI Implementation
- **Status:** Single Global Floating Widget.
- **Verification:** Verified that `App.jsx` mounts the `FloatingChatWidget` globally outside of routing. The widget handles conversation state, auth conditional rendering (hidden on unauthenticated pages), collapsible panel drawer, history rendering, and trip-context dropdown injection.
- **Gaps found:**
  - An empty placeholder file `Assistant.jsx` remains in `frontend/src/pages/` and could be deleted to clean up.

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
