import { useState, useEffect } from "react";
import { Calendar, CreditCard, Compass, CheckCircle2, AlertTriangle, XCircle, Trash2 } from "lucide-react";
import apiClient from "../api/client";

const DESTINATION_IMAGES = {
  Tokyo: "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80",
  Paris: "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=600&q=80",
  London: "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=600&q=80",
  Rome: "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=600&q=80",
  "New York": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=600&q=80",
  Default: "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=600&q=80"
};

function Dashboard() {
  const [bookings, setBookings] = useState([]);
  const [destinations] = useState(["Tokyo", "Paris", "London", "Rome", "New York"]);
  const [hotels, setHotels] = useState([]);
  
  // Form State
  const [selectedDest, setSelectedDest] = useState("");
  const [selectedHotel, setSelectedHotel] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [passportExpiry, setPassportExpiry] = useState("");
  
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

  useEffect(() => {
    fetchBookings();
  }, []);

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

    if (!selectedDest || !selectedHotel || !startDate || !endDate || !passportExpiry) {
      setError("Please fill out all fields.");
      return;
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
    const passport = parseDateLocal(passportExpiry);

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

    if (passport <= today) {
      errors.passportExpiry = "Passport expiry date must be in the future.";
      hasErrors = true;
    }

    if (hasErrors) {
      setFormErrors(errors);
      setError("Please fix the validation errors below.");
      return;
    }

    setSubmitting(true);
    try {
      await apiClient.post("/bookings/", {
        hotel_id: selectedHotel,
        destination: selectedDest,
        start_date: startDate,
        end_date: endDate,
        passport_expiry: passportExpiry,
      });

      setSuccess("Trip booked successfully!");
      // Reset form
      setSelectedDest("");
      setSelectedHotel("");
      setStartDate("");
      setEndDate("");
      setPassportExpiry("");
      setHotels([]);
      setFormErrors({
        startDate: "",
        endDate: "",
        passportExpiry: ""
      });
      
      // Refresh list
      fetchBookings();
    } catch (err) {
      console.error("Failed to book trip:", err);
      setError(err.response?.data?.detail || "Booking failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-8">
      {/* Booking Form and Bookings List layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Book a new trip card */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 h-fit lg:col-span-1">
          <h3 className="text-lg font-semibold mb-4 text-gray-900">Book a New Trip</h3>
          
          {error && <div className="p-3 mb-4 text-sm text-red-600 bg-red-50 rounded-lg border border-red-100">{error}</div>}
          {success && <div className="p-3 mb-4 text-sm text-green-600 bg-green-50 rounded-lg border border-green-100">{success}</div>}

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
                onChange={(e) => setSelectedHotel(e.target.value)}
                required
                disabled={!selectedDest || loadingHotels}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:border-blue-500 disabled:bg-gray-50 disabled:text-gray-400"
              >
                <option value="">
                  {loadingHotels ? "Loading hotels..." : "Select Hotel"}
                </option>
                {hotels.map((hotel) => (
                  <option key={hotel.id} value={hotel.id}>
                    {hotel.name} (${hotel.price_per_night}/night)
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
              <input
                type="date"
                value={passportExpiry}
                onChange={(e) => {
                  setPassportExpiry(e.target.value);
                  setFormErrors(prev => ({ ...prev, passportExpiry: "" }));
                }}
                required
                className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 ${
                  formErrors.passportExpiry ? "border-red-500 text-red-900" : "border-gray-300"
                }`}
              />
              {formErrors.passportExpiry && (
                <p className="text-red-600 text-xs mt-1">{formErrors.passportExpiry}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-blue-500 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-blue-600 transition-colors disabled:opacity-50 shadow-sm"
            >
              {submitting ? "Booking Trip..." : "Confirm Booking"}
            </button>
          </form>
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
