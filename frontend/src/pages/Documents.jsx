import React from "react";
import { Info } from "lucide-react";

function Documents() {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-xl font-bold mb-2">Document Risk Monitor</h2>
      <p className="text-gray-600">
        This feature will analyze your booking dates against visa requirements and passport validity rules.
      </p>
      <div className="mt-6 p-4 bg-blue-50 border border-blue-100 rounded-lg text-blue-800 text-sm flex items-start gap-2">
        <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
        <span>Seeding for step 1 is complete. Once Feature 1 is built, checking details for each booking will be shown here.</span>
      </div>
    </div>
  );
}

export default Documents;
