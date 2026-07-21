import { useState, useEffect } from "react";
import { Users, Plus, Trash2, Compass, RefreshCw, Star, Info, XCircle } from "lucide-react";
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

const AVAILABLE_TAGS = [
  "luxury", "spa", "near-transit", "views", "wifi", "budget", 
  "city-center", "solo-traveler", "mid-range", "family-friendly", 
  "pool", "romantic", "breakfast-included", "bar", "historic", 
  "gym", "garden", "social", "rooftop"
];

function GroupPlanner() {
  const [tripName, setTripName] = useState("");
  const [selectedDest, setSelectedDest] = useState("");
  const [numNights, setNumNights] = useState(3);
  const [members, setMembers] = useState([
    { name: "", budget: "", preferences: [] },
    { name: "", budget: "", preferences: [] }
  ]);

  const [destinations] = useState([
    "Tokyo", "Paris", "London", "Rome", "New York", 
    "Goa", "Manali", "Jaipur", "Udaipur", "Kerala", "Rishikesh", 
    "Andaman", "Lakshadweep", "Ladakh", "Darjeeling",
    "Thailand", "Dubai", "Singapore", "Bali", "Switzerland", "Maldives",
    "Vietnam", "Sri Lanka", "South Korea", "Turkey", "Spain", "Germany"
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // History State
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  
  // Show Cancelled Plans State
  const [showCancelledPlans, setShowCancelledPlans] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  async function fetchHistory(includeCancelled = showCancelledPlans) {
    setLoadingHistory(true);
    try {
      const response = await apiClient.get(
        includeCancelled ? "/group-trips/?status=cancelled" : "/group-trips/?status=active"
      );
      setHistory(response.data);
    } catch (err) {
      console.error("Failed to fetch history:", err);
    } finally {
      setLoadingHistory(false);
    }
  }

  function handleToggleCancelledPlans(e) {
    const checked = e.target.checked;
    setShowCancelledPlans(checked);
    fetchHistory(checked);
  }

  async function handleCancelGroupTrip(e, tripId) {
    e.stopPropagation(); // prevent loading details into form
    setError("");
    setSuccess("");
    if (!window.confirm("Are you sure you want to cancel this group consensus plan?")) {
      return;
    }
    try {
      await apiClient.delete(`/group-trips/${tripId}`);
      setSuccess("Group trip plan cancelled successfully!");
      if (result && result.id === tripId) {
        setResult(null);
      }
      fetchHistory();
    } catch (err) {
      console.error("Failed to cancel group trip plan:", err);
      setError(err.response?.data?.detail || "Failed to cancel plan. Please try again.");
    }
  }

  function addMember() {
    setMembers([...members, { name: "", budget: "", preferences: [] }]);
  }

  function removeMember(index) {
    if (members.length <= 1) return;
    const newMembers = [...members];
    newMembers.splice(index, 1);
    setMembers(newMembers);
  }

  function updateMemberField(index, field, value) {
    const newMembers = [...members];
    newMembers[index][field] = value;
    setMembers(newMembers);
  }

  function toggleTag(index, tag) {
    const newMembers = [...members];
    const currentPrefs = newMembers[index].preferences;
    if (currentPrefs.includes(tag)) {
      newMembers[index].preferences = currentPrefs.filter((t) => t !== tag);
    } else {
      newMembers[index].preferences = [...currentPrefs, tag];
    }
    setMembers(newMembers);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setResult(null);

    // Validate inputs
    if (!tripName || !selectedDest || !numNights || members.length === 0) {
      setError("Please fill in all general fields and add at least one member.");
      return;
    }

    for (let i = 0; i < members.length; i++) {
      if (!members[i].name || !members[i].budget) {
        setError(`Please fill out Name and Budget for Member ${i + 1}.`);
        return;
      }
      if (parseFloat(members[i].budget) <= 0) {
        setError(`Budget for Member ${i + 1} must be positive.`);
        return;
      }
    }

    setSubmitting(true);
    try {
      const payload = {
        trip_name: tripName,
        destination: selectedDest,
        num_nights: parseInt(numNights),
        members: members.map((m) => ({
          name: m.name,
          budget: parseFloat(m.budget),
          preferences: m.preferences
        }))
      };

      const response = await apiClient.post("/group-trips/", payload);
      setResult(response.data);
      setSuccess("Consensus plan generated successfully!");
      fetchHistory(); // refresh list
    } catch (err) {
      console.error("Failed to generate plan:", err);
      setError(err.response?.data?.detail || "Plan generation failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  function handleSelectHistoryItem(trip) {
    setResult(trip);
    // Load back the form state
    setTripName(trip.trip_name);
    setSelectedDest(trip.destination);
    setNumNights(trip.num_nights);
    setMembers(trip.members.map((m) => ({
      name: m.name,
      budget: m.budget.toString(),
      preferences: m.preferences
    })));
    setError("");
    setSuccess("");
  }

  function resetForm() {
    setTripName("");
    setSelectedDest("");
    setNumNights(3);
    setMembers([
      { name: "", budget: "", preferences: [] },
      { name: "", budget: "", preferences: [] }
    ]);
    setResult(null);
    setError("");
    setSuccess("");
  }

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Left Side: Planning Form */}
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-500" />
                <span>Group Trip Consensus Planner</span>
              </h3>
              <button 
                type="button" 
                onClick={resetForm}
                className="text-xs text-blue-600 font-semibold hover:text-blue-700 flex items-center gap-1"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Reset Form</span>
              </button>
            </div>

            {error && <div className="p-3 mb-4 text-sm text-red-600 bg-red-50 rounded-lg border border-red-100">{error}</div>}
            {success && <div className="p-3 mb-4 text-sm text-green-600 bg-green-50 rounded-lg border border-green-100">{success}</div>}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Trip General Info */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Trip Name</label>
                  <input
                    type="text"
                    value={tripName}
                    onChange={(e) => setTripName(e.target.value)}
                    required
                    placeholder="e.g. Summer Escape"
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Destination</label>
                  <select
                    value={selectedDest}
                    onChange={(e) => setSelectedDest(e.target.value)}
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
                  <label className="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Number of Nights</label>
                  <input
                    type="number"
                    min="1"
                    value={numNights}
                    onChange={(e) => setNumNights(parseInt(e.target.value) || 1)}
                    required
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              {/* Members Configuration */}
              <div className="border-t border-gray-100 pt-5 space-y-4">
                <div className="flex justify-between items-center">
                  <h4 className="text-sm font-bold text-gray-700">Travelers & Preferences</h4>
                  <button
                    type="button"
                    onClick={addMember}
                    className="flex items-center gap-1 px-3 py-1.5 bg-blue-50 border border-blue-100 text-blue-600 rounded-lg text-xs font-semibold hover:bg-blue-100 transition-colors shadow-2xs"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add Traveler</span>
                  </button>
                </div>

                <div className="space-y-4">
                  {members.map((member, index) => (
                    <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-150 relative space-y-4">
                      {members.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeMember(index)}
                          className="absolute top-4 right-4 text-gray-400 hover:text-red-500 transition-colors"
                          title="Remove Traveler"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}

                      {/* Member Info Row */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl">
                        <div>
                          <label className="block text-2xs font-bold uppercase tracking-wider text-gray-400 mb-1">Traveler {index + 1} Name</label>
                          <input
                            type="text"
                            value={member.name}
                            onChange={(e) => updateMemberField(index, "name", e.target.value)}
                            required
                            placeholder="e.g. Alice"
                            className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm bg-white focus:outline-none focus:border-blue-500"
                          />
                        </div>
                        <div>
                          <label className="block text-2xs font-bold uppercase tracking-wider text-gray-400 mb-1">Max Budget ($)</label>
                          <input
                            type="number"
                            min="1"
                            value={member.budget}
                            onChange={(e) => updateMemberField(index, "budget", e.target.value)}
                            required
                            placeholder="e.g. 500"
                            className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm bg-white focus:outline-none focus:border-blue-500"
                          />
                        </div>
                      </div>

                      {/* Tag selector */}
                      <div className="space-y-1.5">
                        <label className="block text-2xs font-bold uppercase tracking-wider text-gray-400">Preferences (Select tags)</label>
                        <div className="flex flex-wrap gap-1.5">
                          {AVAILABLE_TAGS.map((tag) => {
                            const isSelected = member.preferences.includes(tag);
                            return (
                              <button
                                type="button"
                                key={tag}
                                onClick={() => toggleTag(index, tag)}
                                className={`px-2.5 py-1 rounded-full text-xs font-medium border transition-colors ${
                                  isSelected
                                    ? "bg-blue-600 border-blue-600 text-white"
                                    : "bg-white border-gray-200 text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                                }`}
                              >
                                {tag}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Button */}
              <button
                type="submit"
                disabled={submitting}
                className="w-full bg-blue-500 text-white py-3 rounded-lg text-sm font-semibold hover:bg-blue-600 transition-colors disabled:opacity-50 shadow-sm flex items-center justify-center gap-2"
              >
                {submitting ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Analyzing Group Consensus...</span>
                  </>
                ) : (
                  <>
                    <Compass className="w-4 h-4" />
                    <span>Calculate Consensus Trip</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Results Panel */}
          {result && (
            <div className="space-y-6">
              <h3 className="text-lg font-bold text-gray-900">Consensus Options Found</h3>
              
              {/* LLM Reasoning Explanation */}
              <div className="bg-blue-50 border border-blue-100 rounded-lg p-5 text-sm text-blue-900 shadow-2xs">
                <div className="flex items-start gap-3">
                  <Compass className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div>
                    <h4 className="font-bold text-blue-900 mb-1">AI Consensus Analysis</h4>
                    <p className="whitespace-pre-line leading-relaxed">{result.reasoning}</p>
                  </div>
                </div>
              </div>

              {/* Recommendations Options Grid */}
              {result.recommended_options.length === 0 ? (
                <div className="text-center p-12 bg-white rounded-lg border border-gray-200 shadow-sm text-gray-500">
                  <p className="font-medium text-lg text-gray-600">No hotels satisfy everyone's budget.</p>
                  <p className="text-sm text-gray-400 mt-1">Try lowering the number of nights or increasing traveler budgets.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {result.recommended_options.map((hotel) => (
                    <div key={hotel.hotel_id} className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden flex flex-col justify-between hover:shadow-md transition-shadow">
                      <div>
                        {/* Header Destination Image */}
                        <div className="relative h-44 bg-gray-100 overflow-hidden">
                          <img 
                            src={hotel.image_url || DESTINATION_IMAGES[result.destination] || DESTINATION_IMAGES.Default} 
                            alt={hotel.name}
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex flex-col justify-end p-4 text-white">
                            <span className="text-2xs font-bold uppercase tracking-widest bg-blue-600 px-2 py-0.5 rounded-sm w-fit mb-1.5">
                              {result.destination}
                            </span>
                            <h4 className="text-base font-bold truncate drop-shadow-xs">{hotel.name}</h4>
                          </div>
                        </div>

                        {/* Details */}
                        <div className="p-4 space-y-4">
                          <p className="text-gray-600 text-xs leading-relaxed">{hotel.description}</p>
                          
                          {/* Price metrics */}
                          <div className="grid grid-cols-2 gap-3 border-y border-gray-100 py-2.5 text-xs">
                            <div>
                              <span className="text-2xs text-gray-400 font-semibold block uppercase">Price Per Night</span>
                              <span className="text-sm font-bold text-gray-900">${hotel.price_per_night}</span>
                            </div>
                            <div className="bg-blue-50 border border-blue-100/50 rounded px-2 py-1 text-right">
                              <span className="text-2xs text-blue-600 font-semibold block uppercase">Per-Person Split</span>
                              <span className="text-sm font-extrabold text-blue-700">${hotel.per_person_cost.toFixed(2)}</span>
                            </div>
                          </div>

                          {/* Member matches list */}
                          <div className="space-y-2">
                            <span className="text-2xs font-bold text-gray-400 uppercase tracking-wider block">Traveler Matches</span>
                            {Object.entries(hotel.member_matches).map(([name, matches]) => (
                              <div key={name} className="flex items-start gap-2 text-2xs">
                                <span className="w-14 font-semibold text-gray-600 truncate mt-0.5">{name}:</span>
                                <div className="flex flex-wrap gap-1 flex-1">
                                  {matches.length > 0 ? (
                                    matches.map((tag) => (
                                      <span key={tag} className="bg-blue-50 text-blue-700 border border-blue-100 px-1.5 py-0.2 rounded-full text-3xs font-medium">
                                        {tag}
                                      </span>
                                    ))
                                  ) : (
                                    <span className="text-gray-400 italic">no matched preferences</span>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Footer */}
                      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between text-2xs text-gray-500">
                        <div className="flex items-center gap-1">
                          <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
                          <span className="font-semibold text-gray-700">{hotel.rating.toFixed(1)}</span>
                        </div>
                        <span>Total Stay Cost: <b>${hotel.total_cost}</b></span>
                        <span className="font-semibold text-blue-600">Overlap: {hotel.score}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Side: History Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex items-center justify-between border-b border-gray-100 pb-2">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">
              {showCancelledPlans ? "Cancelled Plans" : "Past Plans"}
            </h3>
            <label className="inline-flex items-center text-[10px] font-semibold text-gray-500 cursor-pointer">
              <input
                type="checkbox"
                checked={showCancelledPlans}
                onChange={handleToggleCancelledPlans}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-1.5 w-3 h-3"
              />
              Show cancelled
            </label>
          </div>
          
          {loadingHistory ? (
            <div className="p-4 bg-white border border-gray-200 rounded-lg text-center shadow-xs">
              <span className="text-xs text-gray-400 animate-pulse">Loading history...</span>
            </div>
          ) : history.length === 0 ? (
            <div className="p-4 bg-white border border-gray-200 rounded-lg text-center shadow-xs text-gray-400 text-xs">
              <Info className="w-6 h-6 text-gray-300 mx-auto mb-2" />
              <p>No past plans yet.</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-180 overflow-y-auto pr-1">
              {history.map((trip) => (
                <button
                  key={trip.id}
                  onClick={() => handleSelectHistoryItem(trip)}
                  className="w-full text-left bg-white border border-gray-200 rounded-lg p-3 hover:border-blue-400 hover:shadow-xs transition-all flex flex-col gap-2"
                >
                  <div className="flex justify-between items-start">
                    <span className="text-xs font-bold text-gray-900 truncate max-w-36">{trip.trip_name}</span>
                    <span className="text-3xs font-bold uppercase tracking-widest bg-blue-50 text-blue-600 px-1.5 py-0.2 rounded border border-blue-100">
                      {trip.destination}
                    </span>
                  </div>
                  
                  <div className="text-3xs text-gray-500 flex justify-between items-center">
                    <span>{trip.num_nights} nights | {trip.members.length} travelers</span>
                    <span className="text-gray-400">{new Date(trip.created_at).toLocaleDateString()}</span>
                  </div>
                  
                  <div className="text-3xs border-t border-gray-100 pt-1.5 flex justify-between items-center">
                    <span className="text-gray-400">Options: <b>{trip.recommended_options.length}</b></span>
                    {trip.status === "cancelled" ? (
                      <span className="flex items-center gap-0.5 text-red-500 font-semibold bg-red-50 px-1 py-0.5 rounded border border-red-100">
                        <XCircle className="w-2.5 h-2.5" />
                        Cancelled
                      </span>
                    ) : (
                      <div className="flex items-center gap-1.5">
                        <button
                          type="button"
                          onClick={(e) => handleCancelGroupTrip(e, trip.id)}
                          className="text-red-500 hover:text-red-700 hover:bg-red-50 p-1 rounded transition-colors cursor-pointer"
                          title="Cancel Plan"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                        <span className="text-blue-500 font-semibold hover:underline">Load Plan</span>
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default GroupPlanner;
