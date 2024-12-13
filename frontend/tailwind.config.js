/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#000000',
          foreground: '#ffffff'
        },
        secondary: {
          DEFAULT: '#f4f4f5',
          foreground: '#09090b'
        },
        destructive: {
          DEFAULT: '#ef4444',
          foreground: '#ffffff'
        },
        // Add other color variants as needed
        accent: {
          DEFAULT: '#f4f4f5',
          foreground: '#09090b'
        },
        ring: {
          DEFAULT: '#000000'
        }
      }
    },
  },
  plugins: [],
}