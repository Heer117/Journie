import { useState, useEffect } from "react";
import { Calendar, CreditCard, Compass, CheckCircle2, AlertTriangle, XCircle, Trash2, Users, Sparkles } from "lucide-react";
import apiClient from "../api/client";
import ReactMarkdown from "react-markdown";

const DESTINATION_IMAGES = {
  Tokyo: "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80",
  Paris: "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=600&q=80",
  London: "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=600&q=80",
  Rome: "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=600&q=80",
  "New York": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=600&q=80",
  Goa: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80",
  Manali: "https://images.unsplash.com/photo-1626896756165-247e62a149b6?auto=format&fit=crop&w=600&q=80",
  Jaipur: "https://images.unsplash.com/photo-1477584308802-e9c3788ee1a4?auto=format&fit=crop&w=600&q=80",
  Udaipur: "https://images.unsplash.com/photo-1566552881560-0be862a7c445?auto=format&fit=crop&w=600&q=80",
  Kerala: "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=600&q=80",
  Rishikesh: "https://images.unsplash.com/photo-1545638190-2751f8920d23?auto=format&fit=crop&w=600&q=80",
  Thailand: "https://images.unsplash.com/photo-1528181304800-2f1702425221?auto=format&fit=crop&w=600&q=80",
  Dubai: "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=600&q=80",
  Singapore: "https://images.unsplash.com/photo-1525625293386-3f8f99389edd?auto=format&fit=crop&w=600&q=80",
  Bali: "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=600&q=80",
  Switzerland: "https://images.unsplash.com/photo-1506973035872-a4ec16b8e8d9?auto=format&fit=crop&w=600&q=80",
  Maldives: "https://images.unsplash.com/photo-1439066615861-d1af74d74000?auto=format&fit=crop&w=600&q=80",
  Andaman: "https://images.unsplash.com/photo-1589307078059-be1415eab4c3?auto=format&fit=crop&w=600&q=80",
  Lakshadweep: "https://images.unsplash.com/photo-1546548970-71785318a17b?auto=format&fit=crop&w=600&q=80",
  Ladakh: "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=600&q=80",
  Darjeeling: "https://images.unsplash.com/photo-1557002666-61a8828a276f?auto=format&fit=crop&w=600&q=80",
  Vietnam: "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=600&q=80",
  "Sri Lanka": "https://images.unsplash.com/photo-1588598126714-c49b56f8f533?auto=format&fit=crop&w=600&q=80",
  "South Korea": "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?auto=format&fit=crop&w=600&q=80",
  Turkey: "https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?auto=format&fit=crop&w=600&q=80",
  Spain: "https://images.unsplash.com/photo-1543783207-ec64e4d95325?auto=format&fit=crop&w=600&q=80",
  Germany: "https://images.unsplash.com/photo-1467269204594-9661b134dd2b?auto=format&fit=crop&w=600&q=80",
  Default: "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=600&q=80"
};

const DOMESTIC_DESTINATIONS = ["goa", "manali", "jaipur", "udaipur", "kerala", "rishikesh", "andaman", "lakshadweep", "ladakh", "darjeeling"];

function isDomesticDestination(destName) {
  if (!destName) return false;
  return DOMESTIC_DESTINATIONS.includes(destName.trim().toLowerCase());
}

function formatCurrency(price, destName) {
  if (price === undefined || price === null) return "";
  if (isDomesticDestination(destName)) {
    return `₹${Number(price).toLocaleString("en-IN")}`;
  }
  return `$${price}`;
}

function Dashboard() {
  const [bookings, setBookings] = useState([]);
  const [destinations] = useState([
    "Tokyo", "Paris", "London", "Rome", "New York", 
    "Goa", "Manali", "Jaipur", "Udaipur", "Kerala", "Rishikesh", 
    "Andaman", "Lakshadweep", "Ladakh", "Darjeeling",
    "Thailand", "Dubai", "Singapore", "Bali", "Switzerland", "Maldives",
    "Vietnam", "Sri Lanka", "South Korea", "Turkey", "Spain", "Germany"
  ]);
  const [hotels, setHotels] = useState([]);
  
  // Form State
  const [selectedDest, setSelectedDest] = useState("");
  const [selectedHotel, setSelectedHotel] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [passportExpiry, setPassportExpiry] = useState("");

  // Overlap & On-Behalf-Of State
  const [overlapWarning, setOverlapWarning] = useState("");
  const [bookForSomeoneElse, setBookForSomeoneElse] = useState(false);
  const [bookedForName, setBookedForName] = useState("");
  const [bookedForPhone, setBookedForPhone] = useState("");
  const [bookedForRelation, setBookedForRelation] = useState("");
  
  // Inline Form Validation Errors
  const [formErrors, setFormErrors] = useState({
    startDate: "",
    endDate: "",
    passportExpiry: ""
  });
  
  // Status State
  const [loadingBookings, setLoadingBookings] = useState(true);
  const [loadingHotels, setLoadingHotels] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  
  // Show Cancelled Filter State
  const [showCancelled, setShowCancelled] = useState(false);

  // AI Suggestions State
  const [suggestions, setSuggestions] = useState("");
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [suggestionsError, setSuggestionsError] = useState("");

  useEffect(() => {
    fetchBookings();

    // Reload bookings in real-time when chatbot makes modifications
    const handleBookingUpdate = () => {
      fetchBookings();
    };
    window.addEventListener("booking-updated", handleBookingUpdate);
    return () => {
      window.removeEventListener("booking-updated", handleBookingUpdate);
    };
  }, []);

  useEffect(() => {
    let active = true;
    
    async function fetchSuggestions() {
      if (!selectedDest || !startDate || !endDate) {
        setSuggestions("");
        return;
      }
      
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateRegex.test(startDate) || !dateRegex.test(endDate)) {
        return;
      }
      
      const start = new Date(startDate);
      const end = new Date(endDate);
      if (start >= end) {
        return;
      }

      setLoadingSuggestions(true);
      setSuggestionsError("");
      try {
        const response = await apiClient.get(
          `/bookings/suggestions?destination=${encodeURIComponent(selectedDest)}&start_date=${startDate}&end_date=${endDate}`
        );
        if (active) {
          setSuggestions(response.data.suggestions);
        }
      } catch (err) {
        console.error("Failed to fetch suggestions:", err);
        if (active) {
          setSuggestionsError("Failed to fetch travel suggestions.");
        }
      } finally {
        if (active) {
          setLoadingSuggestions(false);
        }
      }
    }

    const delayDebounce = setTimeout(() => {
      fetchSuggestions();
    }, 600);

    return () => {
      active = false;
      clearTimeout(delayDebounce);
    };
  }, [selectedDest, startDate, endDate]);

  async function fetchBookings(includeCancelled = showCancelled) {
    setLoadingBookings(true);
    try {
      const response = await apiClient.get(
        includeCancelled ? "/bookings/?status=cancelled" : "/bookings/?status=active"
      );
      setBookings(response.data);
    } catch (err) {
      console.error("Failed to fetch bookings:", err);
      setError("Failed to load your bookings.");
    } finally {
      setLoadingBookings(false);
    }
  }

  function handleToggleCancelled(e) {
    const checked = e.target.checked;
    setShowCancelled(checked);
    fetchBookings(checked);
  }

  async function handleCancelBooking(bookingId) {
    setError("");
    setSuccess("");
    if (!window.confirm("Are you sure you want to cancel this booking?")) {
      return;
    }
    try {
      await apiClient.delete(`/bookings/${bookingId}`);
      setSuccess("Booking cancelled successfully!");
      fetchBookings();
    } catch (err) {
      console.error("Failed to cancel booking:", err);
      setError(err.response?.data?.detail || "Failed to cancel booking. Please try again.");
    }
  }

  async function handleDestChange(e) {
    const dest = e.target.value;
    setSelectedDest(dest);
    setSelectedHotel("");
    setHotels([]);
    setOverlapWarning("");
    
    if (isDomesticDestination(dest)) {
      setPassportExpiry("N/A");
      setFormErrors(prev => ({ ...prev, passportExpiry: "" }));
    } else if (passportExpiry === "N/A") {
      setPassportExpiry("");
    }
    
    if (!dest) return;

    setLoadingHotels(true);
    try {
      const response = await apiClient.get(`/bookings/hotels?destination=${dest}`);
      setHotels(response.data);
    } catch (err) {
      console.error("Failed to fetch hotels:", err);
      setError("Failed to load hotels for the selected destination.");
    } finally {
      setLoadingHotels(false);
    }
  }

  async function handleBookTrip(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setFormErrors({
      startDate: "",
      endDate: "",
      passportExpiry: ""
    });

    const isDomestic = isDomesticDestination(selectedDest);

    if (!selectedDest || !selectedHotel || !startDate || !endDate || (!isDomestic && !passportExpiry)) {
      setError("Please fill out all fields.");
      return;
    }

    if (bookForSomeoneElse) {
      if (!bookedForName.trim() || !bookedForPhone.trim()) {
        setError("Please enter the guest's Name and Phone Number.");
        return;
      }
    }

    // Front-end date validations
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const parseDateLocal = (dateStr) => {
      const [year, month, day] = dateStr.split("-").map(Number);
      return new Date(year, month - 1, day);
    };

    const start = parseDateLocal(startDate);
    const end = parseDateLocal(endDate);

    let hasErrors = false;
    const errors = { startDate: "", endDate: "", passportExpiry: "" };

    if (start < today) {
      errors.startDate = "Check-in date cannot be in the past.";
      hasErrors = true;
    }

    if (end <= start) {
      errors.endDate = "Check-out date must be strictly after check-in date.";
      hasErrors = true;
    }

    if (!isDomestic) {
      const passport = parseDateLocal(passportExpiry);
      if (passport <= today) {
        errors.passportExpiry = "Passport expiry date must be in the future.";
        hasErrors = true;
      }
    }

    if (hasErrors) {
      setFormErrors(errors);
      setError("Please fix the validation errors below.");
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        hotel_id: selectedHotel,
        destination: selectedDest,
        start_date: startDate,
        end_date: endDate,
        passport_expiry: isDomestic ? "N/A" : passportExpiry,
      };

      if (bookForSomeoneElse) {
        payload.booked_for = {
          name: bookedForName.trim(),
          phone: bookedForPhone.trim(),
          relation: bookedForRelation.trim() || null
        };
      }

      await apiClient.post("/bookings/", payload);

      setSuccess("Trip booked successfully!");
      // Reset form
      setSelectedDest("");
      setSelectedHotel("");
      setStartDate("");
      setEndDate("");
      setPassportExpiry("");
      setHotels([]);
      setOverlapWarning("");
      setBookForSomeoneElse(false);
      setBookedForName("");
      setBookedForPhone("");
      setBookedForRelation("");
      setFormErrors({
        startDate: "",
        endDate: "",
        passportExpiry: ""
      });
      
      // Refresh list
      fetchBookings();
    } catch (err) {
      console.error("Failed to book trip:", err);
      const detail = err.response?.data?.detail;
      if (typeof detail === "string" && detail.includes("overlaps these dates")) {
        setOverlapWarning(detail);
      } else {
        setError(detail || "Booking failed. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-8">
      {/* Booking Form and Bookings List layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column containing form and travel suggestions */}
        <div className="lg:col-span-1 space-y-6 h-fit">
          {/* Book a new trip card */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold mb-4 text-gray-900">Book a New Trip</h3>
          
          {error && <div className="p-3 mb-4 text-sm text-red-600 bg-red-50 rounded-lg border border-red-100">{error}</div>}
          {success && <div className="p-3 mb-4 text-sm text-green-600 bg-green-50 rounded-lg border border-green-100">{success}</div>}

          {overlapWarning && (
            <div className="p-4 mb-4 text-sm bg-amber-50 rounded-lg border border-amber-200 text-amber-900 space-y-3">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <p className="font-medium leading-normal">{overlapWarning}</p>
              </div>
              <div className="border-t border-amber-200 pt-2 flex items-center">
                <label className="inline-flex items-center text-xs font-bold uppercase tracking-wider text-amber-800 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={bookForSomeoneElse}
                    onChange={(e) => {
                      setBookForSomeoneElse(e.target.checked);
                      setError("");
                    }}
                    className="rounded border-amber-300 text-amber-600 focus:ring-amber-500 mr-2"
                  />
                  Booking for someone else?
                </label>
              </div>
            </div>
          )}

          <form onSubmit={handleBookTrip} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Destination</label>
              <select
                value={selectedDest}
                onChange={handleDestChange}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:border-blue-500"
              >
                <option value="">Select Destination</option>
                {destinations.map((dest) => (
                  <option key={dest} value={dest}>{dest}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Hotel</label>
              <select
                value={selectedHotel}
                onChange={(e) => {
                  setSelectedHotel(e.target.value);
                  setOverlapWarning("");
                }}
                required
                disabled={!selectedDest || loadingHotels}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-400"
              >
                <option value="">
                  {loadingHotels ? "Loading hotels..." : "Select Hotel"}
                </option>
                {hotels.map((hotel) => (
                  <option key={hotel.id} value={hotel.id}>
                    {hotel.name} ({formatCurrency(hotel.price_per_night, selectedDest)}/night)
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Start Date</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => {
                    setStartDate(e.target.value);
                    setFormErrors(prev => ({ ...prev, startDate: "" }));
                    setOverlapWarning("");
                  }}
                  required
                  className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 ${
                    formErrors.startDate ? "border-red-500 text-red-900" : "border-gray-300"
                  }`}
                />
                {formErrors.startDate && (
                  <p className="text-red-600 text-xs mt-1">{formErrors.startDate}</p>
                )}
              </div>
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">End Date</label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => {
                    setEndDate(e.target.value);
                    setFormErrors(prev => ({ ...prev, endDate: "" }));
                    setOverlapWarning("");
                  }}
                  required
                  className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 ${
                    formErrors.endDate ? "border-red-500 text-red-900" : "border-gray-300"
                  }`}
                />
                {formErrors.endDate && (
                  <p className="text-red-600 text-xs mt-1">{formErrors.endDate}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Passport Expiry Date</label>
              {isDomesticDestination(selectedDest) ? (
                <div className="w-full bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2 text-xs font-semibold text-emerald-800 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                  <span>Not required for domestic trips within India (Automatic Clearance)</span>
                </div>
              ) : (
                <input
                  type="date"
                  value={passportExpiry === "N/A" ? "" : passportExpiry}
                  onChange={(e) => {
                    setPassportExpiry(e.target.value);
                    setFormErrors(prev => ({ ...prev, passportExpiry: "" }));
                    setOverlapWarning("");
                  }}
                  required
                  className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 ${
                    formErrors.passportExpiry ? "border-red-500 text-red-900" : "border-gray-300"
                  }`}
                />
              )}
              {formErrors.passportExpiry && !isDomesticDestination(selectedDest) && (
                <p className="text-red-600 text-xs mt-1">{formErrors.passportExpiry}</p>
              )}
            </div>

            {overlapWarning && bookForSomeoneElse && (
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-3 animate-in fade-in duration-200">
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500">Guest Information</h4>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Guest Name</label>
                  <input
                    type="text"
                    value={bookedForName}
                    onChange={(e) => setBookedForName(e.target.value)}
                    placeholder="e.g. Alice Smith"
                    required={bookForSomeoneElse}
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm bg-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Guest Phone Number</label>
                  <input
                    type="text"
                    value={bookedForPhone}
                    onChange={(e) => setBookedForPhone(e.target.value)}
                    placeholder="e.g. +1 555-0199"
                    required={bookForSomeoneElse}
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm bg-white focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1">Relation / Notes (Optional)</label>
                  <input
                    type="text"
                    value={bookedForRelation}
                    onChange={(e) => setBookedForRelation(e.target.value)}
                    placeholder="e.g. Spouse, Business partner"
                    className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm bg-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-blue-500 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-blue-600 transition-colors disabled:opacity-50 shadow-sm"
            >
              {submitting ? "Booking Trip..." : "Confirm Booking"}
            </button>
          </form>
        </div>

        {/* AI Travel Suggestions Card */}
        {selectedDest && startDate && endDate && (
          <div className="bg-gradient-to-br from-blue-50/50 to-indigo-50/30 p-4 rounded-xl shadow-xs border border-blue-100 animate-in fade-in duration-200">
            <div className="flex items-center gap-1.5 mb-2 pb-1.5 border-b border-blue-100/50">
              <Sparkles className="w-4 h-4 text-blue-500 flex-shrink-0" />
              <h4 className="text-xs font-bold text-blue-900">Suggestions for {selectedDest}</h4>
            </div>
            
            {loadingSuggestions ? (
              <div className="space-y-2 animate-pulse py-1">
                <div className="h-3 bg-blue-100/80 rounded w-1/3"></div>
                <div className="h-2.5 bg-blue-100/80 rounded w-full"></div>
                <div className="h-2.5 bg-blue-100/80 rounded w-5/6"></div>
              </div>
            ) : suggestionsError ? (
              <p className="text-[11px] text-gray-500">{suggestionsError}</p>
            ) : suggestions ? (
              <div className="max-h-48 overflow-y-auto pr-1 text-xs text-gray-700 leading-relaxed font-sans scroll-thin">
                <ReactMarkdown
                  components={{
                    h1: ({ node, ...props }) => <h1 style={{ fontSize: '0.85rem', fontWeight: 'bold', marginTop: '0.4rem', marginBottom: '0.15rem', display: 'block', color: '#1e3a8a' }} {...props} />,
                    h2: ({ node, ...props }) => <h2 style={{ fontSize: '0.8rem', fontWeight: 'bold', marginTop: '0.35rem', marginBottom: '0.1rem', display: 'block', color: '#1e3a8a' }} {...props} />,
                    h3: ({ node, ...props }) => <h3 style={{ fontSize: '0.75rem', fontWeight: 'bold', marginTop: '0.3rem', marginBottom: '0.08rem', display: 'block', color: '#1e3a8a' }} {...props} />,
                    p: ({ node, ...props }) => <p style={{ marginBottom: '0.25rem', display: 'block' }} {...props} />,
                    ul: ({ node, ...props }) => <ul style={{ listStyleType: 'disc', paddingLeft: '1rem', marginBottom: '0.25rem', display: 'block' }} {...props} />,
                    ol: ({ node, ...props }) => <ol style={{ listStyleType: 'decimal', paddingLeft: '1rem', marginBottom: '0.25rem', display: 'block' }} {...props} />,
                    li: ({ node, ...props }) => <li style={{ marginBottom: '0.15rem', display: 'list-item' }} {...props} />,
                    strong: ({ node, ...props }) => <strong style={{ fontWeight: 'bold', color: '#1e3a8a' }} {...props} />,
                    em: ({ node, ...props }) => <em style={{ fontStyle: 'italic' }} {...props} />,
                    a: ({ node, ...props }) => <a style={{ color: '#2563eb', textDecoration: 'underline' }} target="_blank" rel="noopener noreferrer" {...props} />
                  }}
                >
                  {suggestions}
                </ReactMarkdown>
              </div>
            ) : (
              <p className="text-[11px] text-gray-400">Select dates to load suggestions.</p>
            )}
          </div>
        )}
      </div>

      {/* Bookings List */}
      <div className="lg:col-span-2 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-gray-100 pb-2">
            <h3 className="text-lg font-semibold text-gray-900">
              {showCancelled ? "Your Cancelled Trips" : "Your Scheduled Trips"}
            </h3>
            <label className="inline-flex items-center text-xs font-semibold text-gray-600 cursor-pointer">
              <input
                type="checkbox"
                checked={showCancelled}
                onChange={handleToggleCancelled}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-2"
              />
              Show cancelled trips
            </label>
          </div>

          {loadingBookings ? (
            <div className="flex items-center justify-center p-12 bg-white rounded-lg border border-gray-200 shadow-sm">
              <span className="text-gray-400 text-sm animate-pulse">Loading bookings...</span>
            </div>
          ) : bookings.length === 0 ? (
            <div className="text-center p-12 bg-white rounded-lg border border-gray-200 shadow-sm text-gray-500">
              <Compass className="w-12 h-12 text-gray-400 mx-auto mb-3 animate-spin-slow" />
              <p className="font-medium">No trips booked yet.</p>
              <p className="text-sm text-gray-400 mt-1">Use the form to book your first getaway!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {bookings.map((booking) => (
                <div key={booking.id} className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden flex flex-col justify-between hover:shadow-md transition-shadow">
                  
                  {/* Card Header (Real Destination Image) */}
                  <div className="relative h-32 bg-gray-100 overflow-hidden">
                    <img 
                      src={DESTINATION_IMAGES[booking.destination] || DESTINATION_IMAGES.Default} 
                      alt={booking.destination}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black/40 flex flex-col justify-between p-4 text-white">
                      <div className="flex justify-between items-center">
                        <span className="text-xs font-bold uppercase tracking-widest bg-white/20 backdrop-blur-xs px-2 py-0.5 rounded">
                          {booking.destination}
                        </span>
                        <span className="text-xs text-gray-200">ID: {booking.id.slice(-6)}</span>
                      </div>
                      <h4 className="text-lg font-bold mt-2 truncate drop-shadow-sm">{booking.hotel_name}</h4>
                    </div>
                  </div>

                  {/* Card Body */}
                  <div className="p-4 space-y-3 flex-1 text-sm text-gray-600">
                    <div className="flex items-center text-sm text-gray-600">
                      <Calendar className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0" />
                      <span>
                        <b>Dates:</b> {booking.start_date} to {booking.end_date}
                      </span>
                    </div>
                    
                    <div className="flex items-center text-sm text-gray-600">
                      <CreditCard className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0" />
                      <span>
                        <b>Passport Expiry:</b> {booking.passport_expiry}
                      </span>
                    </div>

                    {booking.booked_for && (
                      <div className="flex items-center text-sm text-gray-600">
                        <Users className="w-4 h-4 text-gray-400 mr-2 flex-shrink-0" />
                        <span>
                          <b>Booked for:</b> {booking.booked_for.name} ({booking.booked_for.relation || "Guest"})
                        </span>
                      </div>
                    )}

                    {/* Document Risk Monitor Status */}
                    {booking.status !== "cancelled" && booking.document_check && (
                      <div className="pt-2 border-t border-gray-100 mt-2 space-y-1.5">
                        <div className="flex items-center justify-between text-xs bg-gray-50 p-2 rounded border border-gray-100">
                          <span className="font-semibold text-gray-500">Document Monitor:</span>
                          {booking.document_check.status === "Ready" ? (
                            <span className="flex items-center gap-1 text-green-600 font-semibold px-2 py-0.5 bg-green-50 rounded border border-green-100">
                              <CheckCircle2 className="w-3.5 h-3.5 text-green-600" />
                              Ready
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-red-600 font-semibold px-2 py-0.5 bg-red-50 rounded border border-red-100">
                              <AlertTriangle className="w-3.5 h-3.5 text-red-600" />
                              Action Needed
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-gray-500 leading-snug line-clamp-2" title={booking.document_check.reason}>
                          {booking.document_check.reason}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Card Footer (Actions/Status) */}
                  <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 flex justify-end items-center">
                    {booking.status === "cancelled" ? (
                      <span className="flex items-center gap-1 text-xs font-semibold text-red-600 px-2 py-1 bg-red-50 rounded border border-red-100 w-full justify-center">
                        <XCircle className="w-3.5 h-3.5" />
                        Cancelled
                      </span>
                    ) : (
                      <button
                        onClick={() => handleCancelBooking(booking.id)}
                        className="flex items-center gap-1 text-xs font-semibold text-red-600 hover:text-white hover:bg-red-600 px-2.5 py-1.5 rounded border border-red-200 transition-colors cursor-pointer"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        Cancel Booking
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default Dashboard;
