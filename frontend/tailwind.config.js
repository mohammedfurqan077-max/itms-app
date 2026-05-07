/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        command: {
          bg: "#071014",
          panel: "#0d1b20",
          panelSoft: "#12252b",
          line: "#25424a",
          text: "#e7f6f8",
          muted: "#8fb0b8",
          green: "#1fd16b",
          red: "#ff4d4d",
          yellow: "#ffd447",
          gray: "#89949a",
          cyan: "#35c9ff"
        }
      },
      boxShadow: {
        signal: "0 0 0 1px rgba(53,201,255,0.18), 0 16px 40px rgba(0,0,0,0.35)"
      }
    }
  },
  plugins: []
};
