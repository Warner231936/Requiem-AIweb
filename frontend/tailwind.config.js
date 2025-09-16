import { fontFamily } from "tailwindcss/defaultTheme";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        midnight: "#0a0f2c",
        nebula: "#3b0a45",
        starlight: "#6a53a4",
      },
      fontFamily: {
        sans: ["Poppins", "Inter", ...fontFamily.sans],
      },
      boxShadow: {
        glow: "0 0 25px rgba(107, 70, 193, 0.45)",
      },
      animation: {
        'pulse-soft': 'pulseSoft 3s ease-in-out infinite',
        'gradient-flow': 'gradient 12s ease infinite',
      },
      keyframes: {
        pulseSoft: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.65 },
        },
        gradient: {
          '0%, 100%': {
            backgroundPosition: '0% 50%',
          },
          '50%': {
            backgroundPosition: '100% 50%',
          },
        },
      },
    },
  },
  plugins: [],
};
