/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta de colores inspirada en anime
        anime: {
          primary: '#FF6B9D',    // Rosa vibrante
          secondary: '#4ECDC4',  // Turquesa
          accent: '#FFE66D',     // Amarillo dorado
          dark: '#1A1A2E',       // Azul oscuro
          darker: '#16213E',     // Azul más oscuro
          light: '#E94560',      // Rojo coral
          purple: '#9B59B6',     // Púrpura
          blue: '#3498DB',       // Azul brillante
        },
        rating: {
          low: '#E74C3C',        // Rojo para rating bajo
          medium: '#F39C12',     // Naranja para rating medio
          high: '#27AE60',       // Verde para rating alto
          excellent: '#9B59B6'   // Púrpura para rating excelente
        }
      },
      fontFamily: {
        'anime': ['Poppins', 'sans-serif'],
        'heading': ['Orbitron', 'monospace'],
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.5s ease-out',
        'fade-in': 'fadeIn 0.3s ease-in',
        'bounce-gentle': 'bounceGentle 2s infinite',
        'pulse-color': 'pulseColor 2s infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #FF6B9D, 0 0 10px #FF6B9D, 0 0 15px #FF6B9D' },
          '100%': { boxShadow: '0 0 10px #FF6B9D, 0 0 20px #FF6B9D, 0 0 30px #FF6B9D' },
        },
        slideUp: {
          '0%': { transform: 'translateY(30px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
        pulseColor: {
          '0%, 100%': { backgroundColor: '#FF6B9D' },
          '50%': { backgroundColor: '#4ECDC4' },
        }
      },
      backdropBlur: {
        xs: '2px',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'anime-gradient': 'linear-gradient(135deg, #FF6B9D 0%, #4ECDC4 50%, #FFE66D 100%)',
        'card-gradient': 'linear-gradient(145deg, rgba(255, 107, 157, 0.1) 0%, rgba(78, 205, 196, 0.1) 100%)',
      }
    },
  },
  plugins: [],
}