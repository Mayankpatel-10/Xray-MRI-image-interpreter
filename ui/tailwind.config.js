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
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14B8A6', // AI Teal
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        medical: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#b9ddfe',
          300: '#7dc2fd',
          400: '#38a2fa',
          500: '#0f85f3',
          600: '#0F4C81', // Deep Medical Blue
          700: '#0c3d69',
          800: '#0a3052',
          900: '#08243d',
        },
        accent: '#22D3EE', // Bright Cyan
      },
      borderRadius: {
        'lg': '1rem',
        'xl': '1.5rem',
        '2xl': '2rem',
        '3xl': '3rem',
      },
      boxShadow: {
        'sm': '0 2px 8px -1px rgba(15, 76, 129, 0.03)',
        'DEFAULT': '0 4px 12px -2px rgba(15, 76, 129, 0.04), 0 2px 6px -1px rgba(15, 76, 129, 0.02)',
        'md': '0 6px 20px -4px rgba(15, 76, 129, 0.06), 0 4px 8px -2px rgba(15, 76, 129, 0.03)',
        'lg': '0 12px 32px -4px rgba(15, 76, 129, 0.08), 0 4px 12px -2px rgba(15, 76, 129, 0.04)',
        'xl': '0 20px 50px -8px rgba(15, 76, 129, 0.1), 0 10px 20px -4px rgba(15, 76, 129, 0.05)',
        '2xl': '0 30px 80px -10px rgba(15, 76, 129, 0.15)',
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
