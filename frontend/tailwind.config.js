/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        soil: {
          50: '#fdf8f6',
          100: '#f2e8e5',
          200: '#eaddd7',
          500: '#8c5e4f',
          800: '#4a2820',
          900: '#2b140f'
        },
        agri: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d'
        }
      }
    },
  },
  plugins: [],
}
