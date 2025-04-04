import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";

function Dashboard() {
  const [stats, setStats] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      const token = localStorage.getItem("token");
      if (!token) {
        navigate("/");
        return;
      }

      try {
        const res = await axios.get("http://127.0.0.1:5000/admin/dashboard", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setStats(res.data);
      } catch (err) {
        alert("Unauthorized or session expired. Please login again.");
        localStorage.removeItem("token");
        navigate("/");
      }
    };

    fetchStats();
  }, [navigate]);

  if (!stats) return <h2>Loading Dashboard...</h2>;

  return (
    <div className="flex bg-gray-100 min-h-screen">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <main className="flex-1">
        {/* Header */}
        <div className="shadow-md p-4 rounded-lg mb-6 bg-blue-900">
          <h2 className="text-xl font-semibold text-white">Dashboard Overview</h2>
        </div>

        {/* Cards Section */}
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-lg shadow-md">
            <h3 className="text-lg font-bold">Employees</h3>
            <p className="text-2xl mt-2">{stats.total_employees}</p>
          </div>
          <div className="bg-white p-5 rounded-lg shadow-md">
            <h3 className="text-lg font-bold">Attendance</h3>
            <p className="text-2xl mt-2">{stats.total_attendance}</p>
          </div>
          <div className="bg-white p-5 rounded-lg shadow-md">
            <h3 className="text-lg font-bold">Logged In</h3>
            <p className="text-2xl mt-2">{stats.today_check_ins}</p>
          </div>
          <div className="bg-white p-5 rounded-lg shadow-md">
            <h3 className="text-lg font-bold">Logged Out</h3>
            <p className="text-2xl mt-2">{stats.pending_check_outs}</p>
          </div>
        </div>

        {/* Table Section */}
        {/* <div className="bg-white p-6 mt-6 rounded-lg shadow-md overflow-x-auto">
          <h3 className="text-lg font-bold mb-4">Recent Transactions</h3>
          <table className="w-full text-left">
            <thead>
              <tr className="border-b bg-blue-900 text-white">
                <th className="py-2 px-3">ID</th>
                <th className="py-2 px-3">Name</th>
                <th className="py-2 px-3">Email</th>
                <th className="py-2 px-3">Phone</th>
                <th className="py-2 px-3">Date</th>
              </tr>
            </thead>
            <tbody>
              {data.transactions.map((item, index) => (
                <tr key={index} className="border-b">
                  <td className="py-2 px-3">{item.id}</td>
                  <td className="py-2 px-3">{item.name}</td>
                  <td className="py-2 px-3">{item.email}</td>
                  <td className="py-2 px-3">{item.phone}</td>
                  <td className="py-2 px-3">{item.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div> */}
        <button onClick={() => {
        localStorage.removeItem("token");
        navigate("/");
      }}>
        Logout
      </button>
      </main>
    </div>
  );
};
export default Dashboard;