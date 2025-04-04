import React, { useState } from "react";
import logo1 from "../assets/logo1.png";
import toggleButton from "../assets/toggle-button.png";

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <aside className={`w-64 bg-blue-900 text-white min-h-screen p-5 fixed transition-all ${isOpen ? "" : "hidden"}`}>
      <div className="flex justify-center">
        <img src={logo1} alt="Logo" className="w-[150px]" />
      </div>
      <button onClick={() => setIsOpen(false)} className="md:hidden text-white">✖</button>
      <nav className="mt-6">
        <ul className="list-none">
          <li><a href="#" className="block py-2 px-3 rounded-lg bg-blue-700">Dashboard</a></li>
          <li><a href="#" className="block py-2 px-3 rounded-lg mt-2 hover:bg-blue-700">Add</a></li>
          <li><a href="#" className="block py-2 px-3 rounded-lg mt-2 hover:bg-blue-700">Edit</a></li>
          <li><a href="#" className="block py-2 px-3 rounded-lg mt-2 hover:bg-blue-700">Settings</a></li>
        </ul>
      </nav>
      <button onClick={() => setIsOpen(!isOpen)} className="absolute top-6 right-6 md:hidden">
        <img src={toggleButton} alt="Toggle Menu" className="w-6" />
      </button>
    </aside>
  );
};

export default Sidebar;