import { useNavigate, useLocation } from "react-router-dom";
import { LayoutDashboard, Shield, Users, Plane, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

function AppLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { name: "Dashboard", path: "/", icon: <LayoutDashboard className="w-5 h-5" /> },
    { name: "Risk Monitor", path: "/documents", icon: <Shield className="w-5 h-5" /> },
    { name: "Consensus Planner", path: "/group-planner", icon: <Users className="w-5 h-5" /> },
  ];

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="flex h-screen bg-gray-50 text-gray-800">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col justify-between">
        <div className="p-6">
          {/* Logo */}
          <div className="flex items-center space-x-2 mb-8 cursor-pointer" onClick={() => navigate("/")}>
            <Plane className="w-6 h-6 text-blue-500 transform -rotate-45" />
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Journie
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-blue-50 text-blue-600"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  }`}
                >
                  <span className="text-base">{item.icon}</span>
                  <span>{item.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* User Profile / Logout Section */}
        {user && (
          <div className="p-4 border-t border-gray-100 flex flex-col space-y-3">
            <div className="flex items-center space-x-3 px-2">
              <div className="w-9 h-9 rounded-full bg-blue-500 text-white flex items-center justify-center font-semibold text-sm shadow-inner">
                {user.name ? user.name.charAt(0).toUpperCase() : "U"}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {user.name}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  Traveler
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 rounded-lg border border-gray-200 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
            >
              <LogOut className="w-4 h-4 text-gray-500" />
              <span>Log Out</span>
            </button>
          </div>
        )}
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8 shadow-sm z-10">
          <h2 className="text-lg font-semibold text-gray-800">
            {menuItems.find((item) => item.path === location.pathname)?.name || "Overview"}
          </h2>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">Live Assistant Grounding Mode: <b>Active</b></span>
          </div>
        </header>

        {/* Page Content */}
        <section className="flex-1 overflow-y-auto p-8">
          {children}
        </section>
      </main>
    </div>
  );
}

export default AppLayout;
