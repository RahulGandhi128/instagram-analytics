/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        instagram: {
          pink: '#E1306C',
          purple: '#833AB4',
          orange: '#FD1D1D',
          yellow: '#F77737',
        }
      }
    },
  },
  plugins: [],
}
