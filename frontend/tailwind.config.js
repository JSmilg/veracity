/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          0: '#111113',
          1: '#18181b',
          2: '#1f1f23',
          3: '#27272b',
        },
        edge: {
          DEFAULT: '#2e2e33',
          hover: '#3f3f46',
        },
        accent: {
          DEFAULT: '#6366f1',
          hover: '#818cf8',
          muted: '#312e81',
        },
        verified: '#22c55e',
        refuted: '#ef4444',
        partial: '#f59e0b',
        pending: '#a1a1aa',
        warm: '#f97316',
        score: {
          excellent: '#22c55e',
          good: '#3b82f6',
          fair: '#f59e0b',
          poor: '#ef4444',
        },
      },
      fontFamily: {
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
        display: ['Instrument Serif', 'Georgia', 'serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.4s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
        'count-up': 'countUp 1s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(12px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        countUp: {
          '0%': { opacity: '0', transform: 'scale(0.5)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      boxShadow: {
        'elevation-1': '0 1px 2px rgba(0,0,0,0.3), 0 1px 3px rgba(0,0,0,0.15)',
        'elevation-2': '0 4px 8px rgba(0,0,0,0.3), 0 2px 4px rgba(0,0,0,0.15)',
        'elevation-3': '0 8px 24px rgba(0,0,0,0.4), 0 4px 8px rgba(0,0,0,0.2)',
      },
    },
  },
  plugins: [],
}
