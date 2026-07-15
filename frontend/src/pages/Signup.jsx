import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Plane, User, Mail, Lock, AlertCircle, Check, Circle } from "lucide-react";

function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({ name: "", email: "", password: "" });
  const [globalError, setGlobalError] = useState("");
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  // Validation checkers
  const validateName = (val) => {
    if (!val.trim()) {
      return "Name is required";
    }
    return "";
  };

  const validateEmail = (val) => {
    if (!val) {
      return "Email address is required";
    }
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!regex.test(val)) {
      return "Enter a valid email address";
    }
    return "";
  };

  const validatePassword = (val) => {
    if (!val) {
      return "Password is required";
    }
    if (val.length < 8) {
      return "Password must be at least 8 characters long";
    }
    if (!/[a-zA-Z]/.test(val) || !/[0-9]/.test(val)) {
      return "Password must contain both letters and numbers";
    }
    if (!/[^a-zA-Z0-9]/.test(val)) {
      return "Password must contain at least one special character";
    }
    return "";
  };

  // Dynamic state checks for password criteria
  const isMinLength = password.length >= 8;
  const hasLetterAndNumber = /[a-zA-Z]/.test(password) && /[0-9]/.test(password);
  const hasSpecialChar = /[^a-zA-Z0-9]/.test(password);

  const handleNameChange = (e) => {
    const val = e.target.value;
    setName(val);
    setErrors((prev) => ({ ...prev, name: validateName(val) }));
  };

  const handleEmailChange = (e) => {
    const val = e.target.value;
    setEmail(val);
    setErrors((prev) => ({ ...prev, email: validateEmail(val) }));
  };

  const handlePasswordChange = (e) => {
    const val = e.target.value;
    setPassword(val);
    setErrors((prev) => ({ ...prev, password: validatePassword(val) }));
  };

  async function handleSubmit(e) {
    e.preventDefault();
    setGlobalError("");

    // Final validation check before submitting
    const nameErr = validateName(name);
    const emailErr = validateEmail(email);
    const passwordErr = validatePassword(password);

    if (nameErr || emailErr || passwordErr) {
      setErrors({ name: nameErr, email: emailErr, password: passwordErr });
      return;
    }

    setLoading(true);
    try {
      await signup(name, email, password);
      navigate("/");
    } catch (err) {
      setGlobalError(err.response?.data?.detail || "Signup failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div 
      className="flex items-center justify-center min-h-screen w-screen bg-cover bg-center bg-no-repeat relative py-8"
      style={{ 
        backgroundImage: `url("https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?auto=format&fit=crop&w=1920&q=80")` 
      }}
    >
      {/* Dark overlay to increase contrast */}
      <div className="absolute inset-0 bg-black/35 z-0"></div>

      <div className="bg-white/90 backdrop-blur-md p-8 rounded-xl shadow-2xl border border-white/20 w-96 space-y-6 z-10 relative">
        {/* Branding header */}
        <div className="flex flex-col items-center space-y-2">
          <div className="flex items-center space-x-2">
            <Plane className="w-8 h-8 text-blue-600 transform -rotate-45" />
            <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Journie
            </span>
          </div>
          <p className="text-gray-500 text-sm">Create your traveler account</p>
        </div>

        {/* Global Error Banner */}
        {globalError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm flex items-start space-x-2">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <span>{globalError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          {/* Name input group */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider block">Full Name</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <User className="w-5 h-5 text-gray-400" />
              </span>
              <input
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={handleNameChange}
                className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                  errors.name 
                    ? "border-red-500 focus:ring-red-200 focus:border-red-500" 
                    : "border-gray-300 focus:ring-blue-100 focus:border-blue-500"
                }`}
              />
            </div>
            {errors.name && (
              <p className="text-red-500 text-xs mt-1 flex items-center space-x-1">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>{errors.name}</span>
              </p>
            )}
          </div>

          {/* Email input group */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider block">Email Address</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <Mail className="w-5 h-5 text-gray-400" />
              </span>
              <input
                type="email"
                placeholder="john@example.com"
                value={email}
                onChange={handleEmailChange}
                className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                  errors.email 
                    ? "border-red-500 focus:ring-red-200 focus:border-red-500" 
                    : "border-gray-300 focus:ring-blue-100 focus:border-blue-500"
                }`}
              />
            </div>
            {errors.email && (
              <p className="text-red-500 text-xs mt-1 flex items-center space-x-1">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>{errors.email}</span>
              </p>
            )}
          </div>

          {/* Password input group */}
          <div className="space-y-1">
            <label className="text-xs font-semibold text-gray-600 uppercase tracking-wider block">Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <Lock className="w-5 h-5 text-gray-400" />
              </span>
              <input
                type="password"
                placeholder="Minimum 8 characters"
                value={password}
                onChange={handlePasswordChange}
                className={`w-full pl-10 pr-3 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                  errors.password 
                    ? "border-red-500 focus:ring-red-200 focus:border-red-500" 
                    : "border-gray-300 focus:ring-blue-100 focus:border-blue-500"
                }`}
              />
            </div>
            {errors.password && (
              <p className="text-red-500 text-xs mt-1 flex items-center space-x-1">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>{errors.password}</span>
              </p>
            )}

            {/* Dynamic Password Strength Indicators */}
            <div className="mt-2.5 p-3 bg-gray-50 border border-gray-100 rounded-lg space-y-1.5">
              <p className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider">Password Requirements</p>
              
              <div className="flex items-center space-x-1.5 text-xs">
                {isMinLength ? (
                  <Check className="w-4 h-4 text-green-600 shrink-0" />
                ) : (
                  <Circle className="w-4 h-4 text-gray-300 shrink-0" />
                )}
                <span className={isMinLength ? "text-green-700 font-medium" : "text-gray-500"}>
                  At least 8 characters
                </span>
              </div>

              <div className="flex items-center space-x-1.5 text-xs">
                {hasLetterAndNumber ? (
                  <Check className="w-4 h-4 text-green-600 shrink-0" />
                ) : (
                  <Circle className="w-4 h-4 text-gray-300 shrink-0" />
                )}
                <span className={hasLetterAndNumber ? "text-green-700 font-medium" : "text-gray-500"}>
                  Contains both letters and numbers
                </span>
              </div>

              <div className="flex items-center space-x-1.5 text-xs">
                {hasSpecialChar ? (
                  <Check className="w-4 h-4 text-green-600 shrink-0" />
                ) : (
                  <Circle className="w-4 h-4 text-gray-300 shrink-0" />
                )}
                <span className={hasSpecialChar ? "text-green-700 font-medium" : "text-gray-500"}>
                  Contains at least one special character
                </span>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium py-2.5 rounded-lg disabled:opacity-50 transition-all shadow-md cursor-pointer mt-3"
          >
            {loading ? "Creating account..." : "Sign up"}
          </button>

          {/* Link to Login */}
          <p className="text-sm text-center text-gray-500 pt-2">
            Already have an account?{" "}
            <Link to="/login" className="text-blue-600 font-semibold hover:underline">
              Log in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}

export default Signup;