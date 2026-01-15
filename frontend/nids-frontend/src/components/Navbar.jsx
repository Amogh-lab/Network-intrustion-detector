import React from "react";

export default function Navbar({ section, setSection }) {
  const menu = ["Dashboard", "System Health", "ML Predictions"];

  return (
    <nav className="w-full fixed top-0 left-0 z-50 bg-[#0f2027]/90 backdrop-blur-md border-b border-white/10 shadow-xl">
      <div className="max-w-7xl mx-auto px-6 py-3 flex justify-center md:justify-around items-center">
        {menu.map((item) => (
          <button
            key={item}
            onClick={() => setSection(item)}
            className={`relative px-4 py-2 text-sm md:text-base font-semibold transition-all
              ${section === item 
                ? "text-[#00fff7] after:absolute after:-bottom-1 after:left-0 after:w-full after:h-0.5 after:bg-[#00fff7] after:rounded-full"
                : "text-white/70 hover:text-[#00fff7]"
              }`}
          >
            {item}
          </button>
        ))}
      </div>
    </nav>
  );
}
