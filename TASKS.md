Read AGENTS.md and PROGRESS.md for full context.

GLOBAL RULES (apply to everything below, stated once):
- No emojis anywhere in the UI
- Real photography for destinations/hotels, never placeholders
- Follow existing conventions: routes/services/schemas separation on backend,
  Tailwind matching existing component style, lucide-react for icons

Work through the following phases IN ORDER. After each phase, stop, report
what you did, and tell me exactly how to manually test it. Wait for my
confirmation before starting the next phase — do not proceed automatically.

PHASE 1 — AUDIT (report only, no changes)
Verify by actually reading the code, not by trusting PROGRESS.md claims:
- Booking flow: search/results, create booking, validation (check-out after
  check-in, no past dates)
- Feature 1 (Document Risk Monitor): is this actually complete, or partially
  built? Report specifically what exists vs what's missing.
- Feature 2 (Group Consensus): confirm still working
- Auth: protected routes genuinely enforcing auth, not just hiding UI
- Chat: does it currently exist in more than one place (sidebar AND floating
  bubble)? Confirm current state.
List every gap found. Do not fix anything yet.

PHASE 2 — COMPLETE FEATURE 1 (if Phase 1 found it incomplete)
- Backend: destination -> minimum passport validity (days) lookup table for
  ~15 common countries; service comparing passport expiry against
  (return_date + min_validity_days); Ready/Action Needed status with specific
  reason; LLM only phrases the explanation, doesn't decide the logic; save to
  document_checks collection
- Frontend: checklist panel component showing status + reason per booking
Show your plan before coding.

PHASE 3 — FIX CHAT UI (single floating widget only)
- Remove any sidebar or dedicated /chat page version of the assistant entirely
- Floating circular button, fixed bottom-right, mounted in App.jsx outside
  <Routes> so it persists across all pages
- Click opens a chat panel/drawer overlaying the current page (not a full
  page navigation); click again or an X closes it
- Preserve all existing chat logic (history, auth) exactly as-is — this is a
  placement change only
Show your component plan (e.g. FloatingChatWidget.jsx wrapping existing
ChatWindow logic) before implementing.

PHASE 4 — FEATURE 3: IN-TRIP LIVE ASSISTANT
- Backend: extend /chat to accept an optional active booking_id; when
  present, inject that booking's context (destination, dates, hotel) into
  the LLM's system context for grounded help with delays, lost luggage,
  medical emergencies, local transport, disruptions
- Frontend: within the floating widget, a dropdown to select an active
  booking for the current chat session (only shown if user has bookings)

PHASE 5 — DELETE/CANCEL FOR BOOKINGS AND GROUP TRIPS
- DELETE /bookings/{booking_id} — protected, owner-only; also clean up
  associated document_checks entries for that booking
- DELETE /group-trips/{trip_id} — protected, organizer-only
- Add a "status" field ("active"/"cancelled"/"completed") to both, so
  cancellation can be a soft-delete (hidden from default view) rather than
  permanent removal; default view shows only "active"; add a simple
  "Show cancelled" checkbox to view the rest
- Frontend: cancel/delete action on booking and group trip cards, with a
  confirmation prompt before deleting

PHASE 6 — MMT COMPARISON (lowest priority, only if time allows)
Use the browser to visit makemytrip.com's hotel booking flow and compare
against our local app (localhost):
- Hotel card layout differences (ratings, amenity icons, pricing display,
  photo quality)
- How their Myra assistant icon/behavior differs from ours
- Any spacing/typography/color choices where ours looks less polished
Report findings only — do not change anything based on this phase without
my explicit confirmation on which specific gaps to close.

Update PROGRESS.md after each phase with what was built/found and how to
test it.