/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-primary': '#00E5FF',
        'cyber-secondary': '#8B5CF6',
        'cyber-accent': '#c9a961',
        'cyber-critical': '#FF4444',
        'cyber-success': '#00FF88',
        'cyber-card': '#071426',
      },
      fontFamily: {
        'heading': ['Cormorant Garamond', 'serif'],
        'body': ['DM Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
