export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        neon: "#00fff7",
        darkbg: "#050510",
        glass: "rgba(255,255,255,0.05)",
      },
      boxShadow: {
        neon: "0 0 25px #00fff7",
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        glow: "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        float: {
          "0%,100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-20px)" },
        },
        glow: {
          from: { boxShadow: "0 0 10px #00fff7" },
          to: { boxShadow: "0 0 30px #00fff7" },
        },
      },
    },
  },
  plugins: [],
};
