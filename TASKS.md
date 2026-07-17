

PHASE 1 — BOOKING DATE OVERLAP VALIDATION + BOOKING ON BEHALF OF SOMEONE ELSE

1. Overlap check: when creating a booking, if the logged-in user already has
   an active booking with overlapping dates (regardless of hotel), show a
   clear warning rather than silently blocking: "You already have a booking
   from [X] to [Y] that overlaps these dates."

2. If this warning appears, show an inline option: "Are you booking this for
   someone else?" If the user confirms yes, reveal additional fields on the
   same form: name, phone number, and an optional relation/note field, for
   who this trip is actually for. Save these as a "booked_for" object on the
   booking document (separate from the logged-in user's own profile) rather
   than overwriting the user's identity — the booking stays owned/created by
   the logged-in account, just tagged with who it's actually for.

   Backend: add this check in the booking creation service; extend the
   booking schema with an optional booked_for field (name, phone,
   relation). Frontend: reveal the extra fields conditionally, only when
   the overlap warning appears and the user opts into "booking for someone
   else" — don't show these fields on every booking by default.

Show me your plan before implementing.

