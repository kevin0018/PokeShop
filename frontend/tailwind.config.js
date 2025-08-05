/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'pokemon': {
          'red': '#dc2626',
          'blue': '#1e40af',
          'yellow': '#facc15',
          'green': '#16a34a',
        }
      }
    },
  },
  plugins: [],
}
