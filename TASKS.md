# Journie — Master Plan (post-mentor-review)

## Global rules (apply to every phase below)
- No emojis anywhere in the UI
- Real photography, never placeholders
- Existing conventions: routes/services/schemas separation, Tailwind
  matching established components
- Prefer genuinely distinct AI/tool usage over one LLM doing everything —
  e.g. a weather API tool, SerpAPI for search/itinerary, LangChain
  agent/tool-calling for booking actions, a separate reasoning step for
  Group Consensus — so the project demonstrates breadth of AI integration,
  not just one repeated chat call
- Update PROGRESS.md and commit with a clear message only after each phase
  is manually confirmed working by me

  GIT WORKFLOW — follow this exactly for every phase:
1. Before starting: git checkout develop, then git checkout -b feature/[phase-name]
   (e.g. feature/phase-a-langchain-refactor)
2. After I confirm the phase works and tell you to commit: stage and commit
   with a clear conventional message (e.g. "feat: refactor LLM calls to use
   LangChain ChatGroq wrapper"), then push the branch
3. Merge into develop: git checkout develop, git merge feature/[phase-name],
   push
4. Merge into main so it reflects on the live deployed site: git checkout
   main, git merge develop, push
5. Confirm afterward by running git log --oneline -5 on main and showing
   me the output, so I can see the merge actually landed

Do NOT skip the merge-to-main step — Render and Netlify are both connected
to the main branch for auto-deploy, so changes only go live once main is
updated. Do not merge to main until I have explicitly confirmed the phase
is tested and approved — never merge automatically right after implementing.

---

## PHASE A — LangChain Foundational Refactor (prerequisite for B-E)
Replace direct Groq SDK usage with LangChain's ChatGroq wrapper in
llm_service.py. Convert conversation memory (currently manual Mongo
load/append/save) to use LangChain message objects (HumanMessage/
AIMessage/SystemMessage) — keep Mongo as the storage layer, just structure
messages LangChain's way. Set up a LangChain agent/tool-calling scaffold
(even with zero tools yet) that Phases B-E will attach tools to. This phase
is infrastructure only — no new user-facing behavior yet.

## PHASE B — Markdown-Formatted Chat Replies (quick, do early)
Frontend: render chatbot replies using a markdown renderer (react-markdown)
instead of plain text, so lists, bold text, headers in LLM responses
display properly. Backend: no change needed if LLM already outputs
markdown-friendly text; confirm prompts don't discourage markdown formatting.

## PHASE C — Full Trip Context + Weather Tool + SerpAPI Tool
Remove the trip-selector dropdown in the chat widget. Instead, give the
agent a get_user_trips tool (LangChain tool) that returns all the user's
past/current/future bookings — the agent decides when to call it based on
the conversation, not a manual UI selector.
Add a get_weather tool (using a free weather API, e.g. Open-Meteo, no key
needed) the agent can call for a destination/date.
Add a search_places tool using SerpAPI (requires a SerpAPI key — flag if we
don't have one yet) for itinerary/hotel/place research the agent can invoke
when a user asks about things to do somewhere.

## PHASE D — Agentic Booking/Cancellation
Give the agent create_booking and cancel_booking tools. The agent should
conversationally gather required info (destination, hotel choice, dates,
passport expiry if international) across multiple turns, confirm with the
user before calling the tool, then execute the booking/cancellation via the
existing booking_service functions wrapped as tools. Reuse existing
validation (overlap check, date validation) inside the tool itself so the
agent can't bypass it.

## PHASE E — AI Itinerary Suggestions During Booking (non-chat)
On the booking form itself (not the chatbot), once a destination and dates
are selected, show AI-generated suggestions: relevant activities/interests
for that destination, and what's notable for that specific season/month
based on the selected dates. This is a direct LLM call triggered by
form state, separate from the conversational agent.

## PHASE F — AI-ify Group Consensus Planner
Current version: deterministic budget/preference filtering + LLM only
writes the explanation. Upgrade: have the LLM take a more active reasoning
role — e.g. handling ambiguous/conflicting preferences intelligently
(not just exact tag matching), or suggesting a compromise when no option
perfectly fits every budget, with reasoning shown. Keep the deterministic
filtering as a safety floor (never recommend something that breaks a hard
budget constraint) — the AI layer adds nuance on top, doesn't replace the
guardrail.

## PHASE G — Home Page (MMT-style)
Hero section: grid/carousel of 6-8 popular destinations using real
Unsplash photo URLs (?w=800 sizing). Optionally ONE muted autoplay hero
video max, rest are photos. Each destination tile is clickable, navigates
to the booking page with that destination pre-selected via query param
(e.g. /book?destination=Goa) — confirm the booking page's dropdown reads
and applies it on load. Below hero: brief showcase of the 3 core features
with lucide-react icons. Show chosen destinations/image URLs before
implementing.

## PHASE H — Expand Destination & Hotel Dataset
Expand seed_hotels.py from ~5 to 15-20 destinations (mix of domestic:
Goa, Manali, Jaipur, Udaipur, Kerala, Rishikesh; international: Thailand,
Dubai, Singapore, Bali, etc). 4-6 hotels per destination with varied
realistic pricing in INR (or local currency for international), ratings,
amenities — not copy-pasted clones. 2-3 curated real photo URLs per
destination, reused across that destination's hotels. Passport/visa
validity logic (Feature 1) should ONLY apply to international
destinations — domestic Indian trips skip the passport/visa check
entirely. Do not wipe existing hotels collection — add alongside what
exists so current bookings stay valid. Update homepage tiles to pull from
this expanded list. Show full destination list before generating data.

## PHASE I — Visa/Passport Upload + Guidance Content
Fix any Document Risk Monitor bugs found in earlier audits first
(boundary dates, missing destinations defaulting to "verify manually").
Add optional passport/visa image upload as a labeled PROTOTYPE feature
(no real OCR, just a stored reference + "document_uploaded: true" flag,
protected storage, visible disclaimer not to upload real documents). Add
static guidance content per destination on "Action Needed" status: typical
application timeline, visa type (e-visa/on-arrival/embassy), processing
time estimate, with links to OFFICIAL government sources only (e.g.
passportindia.gov.in) — no third-party "expediting" sites.

## PHASE J — Mock Payment (stretch, only after A-I confirmed)
Simulated payment only, no real gateway. Simple form (card/expiry/CVV,
no real validation needed), "Processing..." state, then mark booking
"Paid" with a fake transaction ID.

## PHASE K — Business/Hotel Manager Dashboard (stretch, lowest priority)
Flag time estimate explicitly before starting. Minimal scope only: role
field on user model, a simple protected dashboard route for a
"hotel_manager" role, read-only booking visibility + availability toggle
for their hotels. No full multi-tenant system.