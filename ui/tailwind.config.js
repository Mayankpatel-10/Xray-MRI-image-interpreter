/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
        },
        medical: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        accent: '#10B981', // Emerald green
      },
      borderRadius: {
        'lg': '1rem',
        'xl': '1.5rem',
        '2xl': '2rem',
        '3xl': '3rem',
      },
      boxShadow: {
        'sm': '0 2px 8px -1px rgba(13, 148, 136, 0.03)',
        'DEFAULT': '0 4px 12px -2px rgba(13, 148, 136, 0.04), 0 2px 6px -1px rgba(13, 148, 136, 0.02)',
        'md': '0 6px 20px -4px rgba(13, 148, 136, 0.06), 0 4px 8px -2px rgba(13, 148, 136, 0.03)',
        'lg': '0 12px 32px -4px rgba(13, 148, 136, 0.08), 0 4px 12px -2px rgba(13, 148, 136, 0.04)',
        'xl': '0 20px 50px -8px rgba(13, 148, 136, 0.1), 0 10px 20px -4px rgba(13, 148, 136, 0.05)',
        '2xl': '0 30px 80px -10px rgba(13, 148, 136, 0.15)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
