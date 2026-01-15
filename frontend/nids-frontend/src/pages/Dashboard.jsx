import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api } from "../services/api";
import MetricCard from "../components/MetricCard";

export default function Dashboard() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    const res = await api.post("/stop-capture");
    setData(res.data);
  };

  const attacks = data.filter(d => d.state !== "BENIGN").length;

  return (
    <div className="p-10 space-y-8">
      <motion.h1
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-4xl font-bold text-neon"
      >
        🛡️ Network Intrusion Dashboard
      </motion.h1>

      <div className="grid grid-cols-3 gap-6">
        <MetricCard title="Total Flows" value={data.length} color="neon" />
        <MetricCard title="Attacks" value={attacks} color="red-500" />
        <MetricCard title="Benign" value={data.length - attacks} color="green-400" />
      </div>
    </div>
  );
}
