import { useState, useEffect } from "react";
import { Shield, CheckCircle2, AlertTriangle, Calendar, CreditCard, Compass, Loader2 } from "lucide-react";
import apiClient from "../api/client";

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

function Documents() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchBookings();
  }, []);

  async function fetchBookings() {
    setLoading(true);
    try {
      const response = await apiClient.get("/bookings/");
      setBookings(response.data);
    } catch (err) {
      console.error("Failed to fetch bookings for document check:", err);
      setError("Failed to load travel documents.");
    } finally {
      setLoading(false);
    }
  }

  function isPassportValid(expiryDateStr) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const [year, month, day] = expiryDateStr.split("-").map(Number);
    const expiry = new Date(year, month - 1, day);
    return expiry > today;
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-xl font-bold mb-2 flex items-center gap-2 text-gray-900">
          <Shield className="w-6 h-6 text-blue-500" />
          Document Risk Monitor
        </h2>
        <p className="text-gray-600">
          Verify passport validity and visa requirements for all your upcoming bookings. All checks are processed dynamically based on the destination's custom regulations.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-12 bg-white rounded-lg border border-gray-200 shadow-sm">
          <Loader2 className="w-6 h-6 text-blue-500 animate-spin mr-2" />
          <span className="text-gray-400 text-sm">Analyzing travel documents...</span>
        </div>
      ) : error ? (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      ) : bookings.length === 0 ? (
        <div className="text-center p-12 bg-white rounded-lg border border-gray-200 shadow-sm text-gray-500">
          <Compass className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="font-medium">No trips booked yet.</p>
          <p className="text-sm text-gray-400 mt-1">Book a trip from the Dashboard to monitor travel document requirements.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {bookings.map((booking) => {
            const check = booking.document_check || { status: "Action Needed", reason: "Pending analysis." };
            const isReady = check.status === "Ready";
            const isDomestic = ["goa", "manali", "jaipur", "udaipur", "kerala", "rishikesh", "andaman", "lakshadweep", "ladakh", "darjeeling"].includes(booking.destination.toLowerCase());

            return (
              <div key={booking.id} className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden flex flex-col md:flex-row hover:shadow-md transition-shadow">
                {/* Image Section */}
                <div className="relative w-full md:w-64 h-48 md:h-auto bg-gray-100 flex-shrink-0">
                  <img
                    src={DESTINATION_IMAGES[booking.destination] || DESTINATION_IMAGES.Default}
                    alt={booking.destination}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-black/40 flex flex-col justify-end p-4 text-white">
                    <span className="text-xs font-bold uppercase tracking-widest bg-white/20 backdrop-blur-xs px-2 py-0.5 rounded w-fit">
                      {booking.destination}
                    </span>
                    <h3 className="text-lg font-bold mt-1 truncate">{booking.hotel_name}</h3>
                  </div>
                </div>

                {/* Details Section */}
                <div className="p-6 flex-1 flex flex-col justify-between">
                  <div>
                    {/* Header: Title and Status */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                      <div>
                        <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Booking Reference</h4>
                        <p className="text-xs text-gray-500">ID: {booking.id}</p>
                        {booking.booked_for && (
                          <p className="text-xs font-semibold text-blue-600 mt-1">
                            Booked for: {booking.booked_for.name} ({booking.booked_for.relation || "Guest"})
                          </p>
                        )}
                      </div>
                      <div className="flex items-center">
                        {isReady ? (
                          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-green-50 border border-green-200 text-green-700">
                            <CheckCircle2 className="w-4 h-4 text-green-600" />
                            Ready
                          </span>
                        ) : (
                          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-50 border border-red-200 text-red-700">
                            <AlertTriangle className="w-4 h-4 text-red-600" />
                            Action Needed
                          </span>
                        )}
                      </div>
                    </div>

                    {/* LLM phrasing box */}
                    <div className={`p-4 rounded-lg mb-6 border ${isReady ? 'bg-green-50/50 border-green-100 text-green-900' : 'bg-red-50/50 border-red-100 text-red-900'}`}>
                      <p className="text-sm font-medium leading-relaxed">
                        {check.reason}
                      </p>
                    </div>

                    {/* Checklist Panel */}
                    <div className="border-t border-gray-100 pt-4">
                      <h5 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Verification Checklist</h5>
                      <div className="space-y-3">
                        {/* Check 1: Expiry date in the future */}
                        <div className="flex items-start gap-3">
                          {isDomestic || isPassportValid(booking.passport_expiry) ? (
                            <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                          )}
                          <div className="text-sm text-gray-700">
                            <p className="font-semibold">Passport Expiry Status</p>
                            <p className="text-xs text-gray-500">
                              {isDomestic ? "Not required for domestic travel." : `Valid until ${booking.passport_expiry}`}
                            </p>
                          </div>
                        </div>

                        {/* Check 2: Minimum passport validity beyond return date */}
                        <div className="flex items-start gap-3">
                          {isDomestic || isReady ? (
                            <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                          ) : (
                            <AlertTriangle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
                          )}
                          <div className="text-sm text-gray-700">
                            <p className="font-semibold">Destination Validity Requirement</p>
                            <p className="text-xs text-gray-500">
                              {isDomestic ? "Not required for domestic travel." : `Checks if passport is valid long enough past check-out (${booking.end_date})`}
                            </p>
                          </div>
                        </div>

                        {/* Check 3: Visa Information */}
                        <div className="flex items-start gap-3">
                          <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                          <div className="text-sm text-gray-700">
                            <p className="font-semibold">Visa Requirements Checked</p>
                            <p className="text-xs text-gray-500">
                              {isDomestic ? "Not required for domestic travel." : `Regulatory guidelines provided for ${booking.destination}`}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-gray-100 flex flex-wrap gap-x-6 gap-y-2 text-xs text-gray-500">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span>Trip: {booking.start_date} to {booking.end_date}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <CreditCard className="w-4 h-4 text-gray-400" />
                      <span>Passport: {booking.passport_expiry}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default Documents;
