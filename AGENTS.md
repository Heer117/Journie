# Journie — AI Travel Booking Assistant

## Tech stack
- Backend: FastAPI (Python 3.12), MongoDB Atlas (via Motor, async), Groq API (llama-3.3-70b-versatile), JWT auth (python-jose + passlib/bcrypt)
- Frontend: React (Vite), Tailwind CSS, react-router-dom, axios
- Dev environment: Windows, Command Prompt (not PowerShell), venv at backend/venv

## Conventions
- Backend follows routes/ → services/ → schemas/ separation; routes call services, services touch the DB, schemas define request/response shapes
- Run backend: `cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --reload-dir app`
- Run frontend: `cd frontend && npm run dev`
- Auth: JWT in Authorization header, extracted via app/utils/dependencies.py's get_current_user
- Never commit .env; .env.example shows required vars

## Status: Day 4 of 8 complete (as of July 7, presenting July 15)
Done: backend skeleton, MongoDB connection, /chat with persistent conversation memory,
JWT signup/login, protected chat route, React frontend with Login/Signup/ChatWindow,
AuthContext, protected routing.

## Remaining work (in priority order)
1. Feature 1 — Document Risk Monitor: passport expiry + visa requirement checklist
   against booking dates, deterministic Python logic, LLM only phrases the result
2. Booking flow — seed mock hotel data, search/create/view bookings
3. Feature 2 — Group Trip Consensus Planner: multiple travelers enter individual
   budget/preferences, backend scores options against all members, returns
   per-person cost split + reasoning
4. Feature 3 — In-Trip Live Assistant: booking-context-grounded chat for
   post-booking issues (delays, lost luggage, etc.)
5. Deploy: Render (backend) + Vercel (frontend)

## Design direction
Existing UI uses Tailwind with blue-500 accents, rounded-lg cards, clean minimal
forms (see Login.jsx, Signup.jsx, ChatWindow.jsx for the established style — match it).

DESIGN RULES (non-negotiable, apply to all frontend work):
- NEVER use emojis anywhere in UI — not in buttons, headings, status badges,
  empty states, or placeholder text. Use icon libraries (lucide-react) instead.
- Visual style should resemble MakeMyTrip / Booking.com: real destination and
  hotel photography (not illustrations, not gradients-as-hero-images), clean
  card layouts, professional travel-industry aesthetic — not generic "AI app"
  look.
- Use lucide-react for all icons (checkmarks, warnings, calendar, location pins,
  etc.) — never emoji characters as icon substitutes.
- For destination/hotel images, use real photo URLs (Unsplash source API or
  curated static URLs), never placeholder gradient boxes or illustrations.