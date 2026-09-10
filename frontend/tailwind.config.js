/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          950: '#0b0f19',
          900: '#111827',
          850: '#151d30',
          800: '#1e293b',
          700: '#334155',
        },
        emerald: {
          500: '#10b981',
          400: '#34d399',
        },
        rose: {
          500: '#f43f5e',
          400: '#fb7185',
        },
        amber: {
          500: '#f59e0b',
          400: '#fbbf24',
        },
        cyan: {
          500: '#06b6d4',
          400: '#22d3ee',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
