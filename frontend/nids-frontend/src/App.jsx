import { useEffect, useState, useRef } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Radar, RadarChart, PolarGrid, PolarAngleAxis
} from "recharts";
import { AnimatePresence, motion } from "framer-motion";
import jsPDF from "jspdf";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

export default function App() {
  const [section, setSection] = useState("Dashboard");
  const [data, setData] = useState([]);
  const [status, setStatus] = useState("Idle");
  const [history, setHistory] = useState([]);
  const [cpuHistory, setCpuHistory] = useState([]);
  const [memoryHistory, setMemoryHistory] = useState([]);
  const [portsServices, setPortsServices] = useState([]);
  const [alert, setAlert] = useState(null); 
  const pdfRef = useRef();

  // --- Logic for ML Visualization ---
  const attackDistribution = [
    { name: "BENIGN", value: data.filter(d => d.attack === "BENIGN").length || 1 },
    { name: "MALICIOUS", value: data.filter(d => d.attack !== "BENIGN").length },
  ];

  const radarData = [
    { subject: 'DDoS', A: data.filter(d => d.attack.includes("DDoS")).length * 10 || 5 },
    { subject: 'BruteForce', A: data.filter(d => d.attack.includes("Brute")).length * 10 || 5 },
    { subject: 'Botnet', A: data.filter(d => d.attack.includes("Bot")).length * 10 || 5 },
    { subject: 'Infiltration', A: data.filter(d => d.attack.includes("Infil")).length * 10 || 5 },
    { subject: 'PortScan', A: data.filter(d => d.attack.includes("Scan")).length * 10 || 5 },
  ];

  const PIE_COLORS = ["#00fff7", "#ff4d4d"];

  const triggerAlert = (flow) => {
    setAlert(flow);
    setTimeout(() => setAlert(null), 5000);
  };

  const simulateAttack = () => {
    const fakeAttack = {
      time: new Date().toLocaleTimeString(),
      port: 443,
      attack: "DDoS-ATTACK-SIMULATED",
      fwdPackets: 500,
      bwdPackets: 200
    };
    setData(prev => [...prev, fakeAttack]);
    triggerAlert(fakeAttack);
  };

  // Fetch live data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/live-data");
        const json = await res.json();
        if (json.length > data.length) {
          const newEntry = json[json.length - 1];
          if (newEntry.attack !== "BENIGN") triggerAlert(newEntry);
        }
        setData(json);
        setStatus("Monitoring Live Traffic");
        const totalPackets = json.reduce((sum, flow) => sum + (flow.fwdPackets || 0) + (flow.bwdPackets || 0), 0);
        setHistory(prev => [...prev.slice(-19), { time: new Date().toLocaleTimeString(), packets: totalPackets }]);
      } catch (err) {
        console.error(err);
        setStatus("Error fetching data");
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, [data.length]);

  // Mock CPU & Memory usage
  useEffect(() => {
    const interval = setInterval(() => {
      const cpu = Math.floor(Math.random() * 60) + 20;
      const memory = Math.floor(Math.random() * 70) + 20;
      const time = new Date().toLocaleTimeString();
      setCpuHistory(prev => [...prev.slice(-19), { time, value: cpu }]);
      setMemoryHistory(prev => [...prev.slice(-19), { time, value: memory }]);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Fetch Active Ports & Services
  useEffect(() => {
    const fetchPortsServices = async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/ports-services");
        const json = await res.json();
        setPortsServices(json);
      } catch (err) {
        console.error(err);
      }
    };
    fetchPortsServices();
    const interval = setInterval(fetchPortsServices, 5000);
    return () => clearInterval(interval);
  }, []);

  const activePorts = new Set(data.map(flow => flow.port)).size;
  const threatLevel = data.some(flow => flow.attack && flow.attack !== "BENIGN") ? "HIGH" : "LOW";

  // PDF export (RESTORED TO ORIGINAL LOGIC)
  const exportPDF = () => {
    const pdf = new jsPDF("landscape", "pt", "a4");
    pdf.setFillColor(15, 32, 39);
    pdf.rect(0, 0, pdf.internal.pageSize.width, 50, "F");
    pdf.setFontSize(26);
    pdf.setTextColor(0, 255, 247);
    pdf.text("NIDS ML Report", 40, 35);
    pdf.setFontSize(12);
    pdf.setTextColor(255, 255, 255);
    pdf.text(`Generated: ${new Date().toLocaleString()}`, pdf.internal.pageSize.width - 200, 35);

    const cardY = 70;
    const cardHeight = 50;
    const cardWidth = 180;
    const gap = 20;
    const stats = [
      { label: "Active Ports", value: activePorts, color: "#00fff7" },
      { label: "Threat Level", value: threatLevel, color: threatLevel === "HIGH" ? "#ff4d4d" : "#4dff88" },
      { label: "Total Packets", value: history[history.length - 1]?.packets || 0, color: "#ffb84d" }
    ];
    stats.forEach((s, i) => {
      pdf.setFillColor(25, 25, 35);
      pdf.roundedRect(40 + i * (cardWidth + gap), cardY, cardWidth, cardHeight, 10, 10, "F");
      pdf.setTextColor(s.color);
      pdf.setFontSize(14);
      pdf.text(`${s.label}: ${s.value}`, 50 + i * (cardWidth + gap), cardY + 32);
    });

    const startY = cardY + cardHeight + 30;
    pdf.setFillColor(0, 255, 247, 20);
    pdf.rect(40, startY, 720, 25, "F");
    pdf.setTextColor(0, 0, 0);
    pdf.setFontSize(14);
    pdf.text("Time", 50, startY + 17);
    pdf.text("Port", 250, startY + 17);
    pdf.text("Attack", 450, startY + 17);

    let y = startY + 25;
    data.forEach((row, i) => {
      pdf.setFillColor(i % 2 === 0 ? 15 : 25, 32, 43);
      pdf.rect(40, y, 720, 25, "F");
      pdf.setTextColor(row.attack === "BENIGN" ? 0 : 255, row.attack === "BENIGN" ? 255 : 77, 64);
      pdf.text(row.time, 50, y + 17);
      pdf.text(String(row.port), 250, y + 17);
      pdf.text(row.attack, 450, y + 17);
      y += 25;
      if (y > 520) { pdf.addPage(); y = 50; }
    });
    pdf.save(`ML_Predictions_${new Date().toLocaleDateString()}.pdf`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f2027] via-[#203a43] to-[#2c5364] text-white pt-20 px-6 relative overflow-x-hidden">
      
      <Navbar section={section} setSection={setSection} />

      {/* Live Alert Notification */}
      <AnimatePresence>
        {alert && (
          <motion.div initial={{ opacity: 0, x: 100 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 100 }} className="fixed top-24 right-6 z-50 bg-red-600/90 border border-red-400 p-4 rounded-2xl shadow-2xl backdrop-blur-md">
            <h4 className="font-black text-white flex items-center gap-2"><span className="animate-ping">⚠️</span> THREAT DETECTED</h4>
            <p className="text-xs text-white/90 font-mono mt-1">{alert.attack} on Port {alert.port}</p>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="absolute w-96 h-96 bg-cyan-500/10 rounded-full blur-[120px] -top-40 -left-40 animate-pulse"></div>
      <div className="absolute w-96 h-96 bg-purple-500/10 rounded-full blur-[120px] -bottom-40 -right-40 animate-pulse"></div>

      <AnimatePresence mode="wait">
        {section === "Dashboard" && (
          <motion.div key="dashboard" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="flex flex-col gap-8 pb-10">
            {/* Hero Header */}
            <motion.div className="bg-white/5 backdrop-blur-xl p-8 rounded-3xl border border-white/10 shadow-2xl relative overflow-hidden">
               <div className="relative z-10">
                <div className="flex items-center gap-3 mb-2">
                  <span className="px-3 py-1 bg-neon/20 text-neon text-xs font-bold rounded-full border border-neon/30 animate-pulse">SYSTEM ACTIVE</span>
                  <span className="text-white/40 text-xs font-mono">ID: NIDS-AX-99</span>
                </div>
                <h1 className="text-6xl font-black text-white drop-shadow-2xl mb-4 tracking-tight">
                  <span className="text-neon">Smart</span> NIDS Dashboard
                </h1>
                <p className="text-white/60 text-lg max-w-3xl leading-relaxed">
                  Real-time network intrusion detection system leveraging machine learning to classify traffic 
                  and monitor port security across active socket layers.
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                {[ { title: "Real-time", desc: "Live Traffic Analysis", color: "border-purple-500/50"}, { title: "ML Core", desc: "Pattern Classification", color: "border-neon/50"}, { title: "Network", desc: "Socket Monitoring", color: "border-cyan-500/50"} ].map((item, i) => (
                  <motion.div key={i} whileHover={{ y: -5 }} className={`bg-white/5 p-5 rounded-2xl border-l-4 ${item.color} backdrop-blur-md`}>
                    <h3 className="font-bold text-xl">{item.title}</h3>
                    <p className="text-white/40 text-sm">{item.desc}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
                <motion.div whileHover={{ scale: 1.02 }} className="bg-glass p-6 rounded-3xl border border-white/10 shadow-xl flex flex-col justify-center items-center text-center">
                   <h3 className="text-white/50 text-xs uppercase tracking-tighter mb-1">Active Ports</h3>
                   <span className="text-4xl font-black text-neon">{activePorts}</span>
                </motion.div>
                <motion.div whileHover={{ scale: 1.02 }} className="bg-glass p-6 rounded-3xl border border-white/10 shadow-xl flex flex-col justify-center items-center text-center">
                   <h3 className="text-white/50 text-xs uppercase tracking-tighter mb-1">Threat Status</h3>
                   <span className={`text-4xl font-black ${threatLevel === "HIGH" ? "text-red-500 animate-pulse" : "text-green-400"}`}>{threatLevel}</span>
                </motion.div>
                <motion.div whileHover={{ scale: 1.02 }} className="bg-glass p-6 rounded-3xl border border-white/10 shadow-xl flex flex-col justify-center items-center text-center">
                   <h3 className="text-white/50 text-xs uppercase tracking-tighter mb-1">Total Packets</h3>
                   <span className="text-4xl font-black text-orange-400">{history[history.length - 1]?.packets || 0}</span>
                </motion.div>
                <div className="md:col-span-3 bg-black/40 border border-white/5 rounded-3xl p-8 h-48 relative overflow-hidden">
                  <div className="flex items-end justify-between h-full gap-1 pt-10">
                    {Array.from({ length: 50 }).map((_, i) => (
                      <motion.div key={i} animate={{ height: [Math.random() * 20 + 10, Math.random() * 80 + 20, Math.random() * 30 + 10] }} transition={{ repeat: Infinity, duration: 2, delay: i * 0.05 }} className="flex-1 bg-gradient-to-t from-transparent via-neon/20 to-neon/60 rounded-full" />
                    ))}
                  </div>
                </div>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-3xl p-6 flex flex-col">
                <h3 className="text-sm font-bold uppercase tracking-widest text-white/80 mb-4 flex justify-between"><span>Live Events</span><span className="text-neon text-[10px]">REAL-TIME</span></h3>
                <div className="flex-1 space-y-4 overflow-y-auto max-h-[400px] pr-2 scrollbar-hide">
                  {data.slice(-8).reverse().map((log, i) => (
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} key={i} className="bg-black/20 p-3 rounded-xl border border-white/5">
                      <div className="flex justify-between text-[10px] mb-1"><span className="text-white/40">{log.time}</span><span className={log.attack === "BENIGN" ? "text-green-500" : "text-red-500"}>{log.attack}</span></div>
                      <div className="text-xs font-mono">Inbound Port: {log.port}</div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* ---------------- System Health (EXACT ORIGINAL RESTORED) ---------------- */}
        {section === "System Health" && (
          <motion.div key="system" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[{ title: "CPU Usage", data: cpuHistory, color: "#ff4d6d" }, { title: "Memory Usage", data: memoryHistory, color: "#4dff88" }, { title: "Network Packets/sec", data: history, color: "#00fff7" }].map((card, i) => (
              <motion.div key={i} className="bg-glass backdrop-blur-xl p-6 rounded-3xl border border-white/10 shadow-2xl hover:scale-105 transition-all duration-500">
                <h2 className="text-2xl mb-4 text-neon font-extrabold drop-shadow-neon">{card.title}</h2>
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={card.data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#555555"/>
                    <XAxis dataKey="time" stroke="#00fff7"/>
                    <YAxis stroke={card.color} unit="%"/>
                    <Tooltip contentStyle={{ backgroundColor: "#0f2027", border: `1px solid ${card.color}` }}/>
                    <Line type="monotone" dataKey={card.title === "Network Packets/sec" ? "packets" : "value"} stroke={card.color} strokeWidth={3} dot={{ r: 3, fill: card.color }}/>
                  </LineChart>
                </ResponsiveContainer>
              </motion.div>
            ))}
            <motion.div className="bg-glass backdrop-blur-xl p-6 rounded-3xl border border-white/10 shadow-2xl hover:scale-105 transition-all duration-500 flex flex-col justify-between">
              <h2 className="text-2xl mb-4 text-neon font-extrabold drop-shadow-neon">System Summary</h2>
              <div className="space-y-4">
                <div className="flex justify-between text-white/80 hover:text-[#00fff7] transition-all"><span>Avg CPU:</span><span>{Math.round(cpuHistory.reduce((a,c)=>a+c.value,0)/Math.max(cpuHistory.length,1))}%</span></div>
                <div className="flex justify-between text-white/80 hover:text-[#00fff7] transition-all"><span>Avg Memory:</span><span>{Math.round(memoryHistory.reduce((a,c)=>a+c.value,0)/Math.max(memoryHistory.length,1))}%</span></div>
                <div className="flex justify-between text-white/80 hover:text-[#00fff7] transition-all"><span>Active Ports:</span><span>{activePorts}</span></div>
                <div className="flex justify-between text-white/80 hover:text-[#00fff7] transition-all"><span>Threat Level:</span><span className={threatLevel==="HIGH"?"text-red-400 font-bold":"text-green-400 font-bold"}>{threatLevel}</span></div>
              </div>
            </motion.div>
            <motion.div className="md:col-span-4 bg-glass backdrop-blur-xl p-6 rounded-3xl border border-white/10 shadow-2xl mt-4 overflow-y-auto max-h-[300px]">
              <h2 className="text-2xl mb-4 text-neon font-extrabold drop-shadow-neon">Active Ports & Services</h2>
              <table className="w-full text-sm border-separate border-spacing-0">
                <thead className="bg-black/40"><tr><th className="p-3 text-left">Port</th><th className="p-3 text-left">Service / App</th></tr></thead>
                <tbody>{portsServices.map((row,i)=>(<tr key={i} className={`hover:bg-neon/10 transition-all ${i%2===0?"bg-black/20":"bg-black/10"}`}><td className="p-3 font-mono">{row.port}</td><td className="p-3">{row.service}</td></tr>))}</tbody>
              </table>
            </motion.div>
          </motion.div>
        )}

        {/* ---------------- ML Predictions (New Analytics Included) ---------------- */}
        {section === "ML Predictions" && (
          <motion.div key="ml" initial={{ opacity:0, y: 20 }} animate={{ opacity:1, y: 0 }} className="flex flex-col xl:flex-row gap-6 w-full pb-10">
            <div className="xl:w-2/3 bg-black/40 backdrop-blur-2xl p-6 rounded-3xl border border-white/10 shadow-2xl flex flex-col">
              <div className="flex justify-between items-center mb-6">
                <div><h2 className="text-3xl font-black text-neon drop-shadow-neon">Classification Engine</h2></div>
                <div className="flex gap-3">
                  <button onClick={simulateAttack} className="px-4 py-2 bg-purple-600/20 border border-purple-500/50 text-purple-400 rounded-lg text-xs font-bold hover:bg-purple-600/40 transition-all">Simulate Attack</button>
                  <button onClick={exportPDF} className="px-6 py-2 bg-neon text-black rounded-lg font-bold hover:scale-105 transition-all">PDF Report</button>
                </div>
              </div>
              <div className="overflow-y-auto max-h-[500px]">
                <table className="w-full text-sm">
                  <thead className="bg-white/5 sticky top-0"><tr className="text-white/50 text-left"><th className="p-4">Timestamp</th><th className="p-4">Port</th><th className="p-4">ML Label</th><th className="p-4">Confidence</th></tr></thead>
                  <tbody>{data.slice().reverse().map((row, i) => (
                    <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-all">
                      <td className="p-4 font-mono text-xs opacity-60">{row.time}</td>
                      <td className="p-4 font-mono text-neon">{row.port}</td>
                      <td className={`p-4 font-black ${row.attack === "BENIGN" ? "text-green-400" : "text-red-500 animate-pulse"}`}>{row.attack}</td>
                      <td className="p-4"><div className="flex items-center gap-2"><div className="flex-1 h-1 bg-white/10 rounded-full overflow-hidden"><div className="h-full bg-neon" style={{ width: row.attack === "BENIGN" ? '98%' : '94%' }}></div></div><span className="text-[10px] text-white/40">98%</span></div></td>
                    </tr>
                  ))}</tbody>
                </table>
              </div>
            </div>
            <div className="xl:w-1/3 flex flex-col gap-6">
              <div className="bg-white/5 p-6 rounded-3xl border border-white/10">
                <h3 className="text-sm font-bold text-white/60 mb-4 uppercase">Attack Vector Analysis</h3>
                <ResponsiveContainer width="100%" height={200}><RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}><PolarGrid stroke="#ffffff20" /><PolarAngleAxis dataKey="subject" tick={{ fill: "#00fff7", fontSize: 10 }} /><Radar name="Threat" dataKey="A" stroke="#ff4d4d" fill="#ff4d4d" fillOpacity={0.5} /></RadarChart></ResponsiveContainer>
              </div>
              <div className="bg-white/5 p-6 rounded-3xl border border-white/10">
                <h3 className="text-sm font-bold text-white/60 mb-2 uppercase">Classification Ratio</h3>
                <ResponsiveContainer width="100%" height={150}><PieChart><Pie data={attackDistribution} innerRadius={40} outerRadius={60} paddingAngle={5} dataKey="value">{attackDistribution.map((entry, index) => (<Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />))}</Pie><Tooltip /></PieChart></ResponsiveContainer>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      <Footer />
    </div>
  );
}