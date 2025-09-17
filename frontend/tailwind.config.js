/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#977BB8',
        'secondary': '#2B1A16',
        'accent': '#543C7C',
      }
    },
  },
  plugins: [],
}
