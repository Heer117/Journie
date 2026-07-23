# Journie — Next Actions Plan

## 1. Recently Completed & Merged to Main
We have successfully completed, manually verified, and merged the following phases into the `main` branch, pushed to production:
- **Phase A**: LangChain Foundational Refactor (ChatGroq, memory serialization).
- **Phase B**: Markdown-formatted chat replies using `react-markdown` on the frontend.
- **Phase C**: Full trip context (`get_user_trips` tool) and weather forecast API integration (`get_weather`).
- **Phase D**: Agentic booking/cancellation with real-time Dashboard synchronization:
  - Added `create_booking` and `cancel_booking` tools.
  - Custom events synchronizing chat drawer closing/cancellation actions directly to Dashboard cards without page refreshes.
  - Fixed Groq API token size limits (TPM 6k max) by truncating conversation history to the last 12 messages.
  - Programmatically forced markdown formatting for tool execution responses so booking lists and weather forecasts are never hidden.
  - Implemented failed_generation key-value regex recovery logic to capture python-style argument calls.
- **Phase E**: AI Travel suggestions during booking (decoupled, season-based recommendations panel on the manual booking form).
- **Phase F**: AI-ify Group Consensus Planner (semantic preference matching, budget compromise analysis, custom reasoning explanations).
- **Phase H**: Seeding of 17 domestic & international destinations and 68 hotels with coordinate mapping and domestic document bypasses.

---

## 2. Remaining Development Scope (In Priority Order)

### Phase G — Home Page (MMT-Style)
- **Status**: Not started.
- **Requirements**:
  - Implement a premium MakeMyTrip / Booking.com style landing page.
  - Grid/carousel showcase of 6-8 popular destinations using high-quality curated Unsplash image URLs.
  - Clickable destination tiles that redirect to the Booking page with the destination pre-selected via query parameter (e.g. `/book?destination=Paris`).
  - Below hero section: clean feature cards demonstrating the 3 core features (Document Risk Monitor, Group Planner, Live Chat Assistant) with `lucide-react` icons.

### Phase I — Visa/Passport Upload + Guidance Content
- **Status**: Partially completed (document risk checks are live, upload & guidance content are pending).
- **Requirements**:
  - Add optional passport & visa image upload form field as a labeled prototype (fake visual upload + status flag, no actual OCR, visual warning not to upload real sensitive documents).
  - Add static country-specific visa guidance links and timelines for "Action Needed" destinations, referencing official government sources (e.g., `passportindia.gov.in`).

### Phase J — Mock Payment (Stretch Feature)
- **Status**: Not started.
- **Requirements**:
  - Simulated payment checkout screen during booking.
  - Inputs for card number, expiry, CVV (basic format validation).
  - "Processing..." loading spinner state.
  - Successful confirmation window flagging the booking status as "Paid" with a generated transaction ID.

### Phase K — Business/Hotel Manager Dashboard (Stretch Feature)
- **Status**: Not started.
- **Requirements**:
  - Add `role` field (e.g. `customer` or `hotel_manager`) to user database schema.
  - Minimal manager-only dashboard route to view bookings for their specific hotels and toggle hotel active/inactive availability.

---

## 3. Immediate Next Steps
1. **Initiate Phase G (MMT-Style Home Page)**: Create a new frontend page/component for the landing page, update paths in `App.jsx` to load this page as `/` (routing existing dashboard/booking flows to `/dashboard` or `/book`), and wire up destination query-param loading.
2. **Setup Git Branch**: Checkout a new branch `feature/phase-g-homepage` to keep changes cleanly isolated.
