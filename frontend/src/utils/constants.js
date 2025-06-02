// src/utils/constants.js

/**
 * Constantes globales de la aplicación
 */

// Configuración de la aplicación
export const APP_CONFIG = {
  NAME: 'Anime Recommendations',
  VERSION: '1.0.0',
  DESCRIPTION: 'Sistema de recomendaciones de anime inteligente',
  AUTHOR: 'Tu Nombre',
}

// Límites y configuraciones de búsqueda
export const SEARCH_CONFIG = {
  MIN_QUERY_LENGTH: 2,
  MAX_QUERY_LENGTH: 100,
  DEBOUNCE_DELAY: 500, // milisegundos
  MAX_RECOMMENDATIONS: 50,
  DEFAULT_RECOMMENDATIONS: 10,
}

// Categorías de rating con configuración visual
export const RATING_CATEGORIES = {
  excellent: {
    label: 'Excelente',
    color: '#9B59B6',
    bgColor: 'bg-rating-excellent',
    textColor: 'text-rating-excellent',
    min: 8.5,
    max: 10,
    icon: '⭐',
    description: 'Obra maestra'
  },
  high: {
    label: 'Muy Bueno',
    color: '#27AE60',
    bgColor: 'bg-rating-high',
    textColor: 'text-rating-high',
    min: 7.0,
    max: 8.4,
    icon: '🌟',
    description: 'Altamente recomendado'
  },
  medium: {
    label: 'Bueno',
    color: '#F39C12',
    bgColor: 'bg-rating-medium',
    textColor: 'text-rating-medium',
    min: 5.0,
    max: 6.9,
    icon: '⚡',
    description: 'Vale la pena ver'
  },
  low: {
    label: 'Regular',
    color: '#E74C3C',
    bgColor: 'bg-rating-low',
    textColor: 'text-rating-low',
    min: 0,
    max: 4.9,
    icon: '❌',
    description: 'Considera otras opciones'
  }
}

// Estados de carga y mensajes
export const UI_MESSAGES = {
  LOADING: {
    SEARCHING: 'Buscando recomendaciones...',
    PROCESSING: 'Procesando datos...',
    LOADING_MORE: 'Cargando más resultados...',
  },
  SUCCESS: {
    RECOMMENDATIONS_FOUND: 'Recomendaciones encontradas',
    SEARCH_COMPLETED: 'Búsqueda completada exitosamente',
  },
  ERROR: {
    NETWORK_ERROR: 'Error de conexión. Verifica tu internet.',
    ANIME_NOT_FOUND: 'No se encontró el anime especificado.',
    NO_RECOMMENDATIONS: 'No se encontraron recomendaciones para este anime.',
    INVALID_INPUT: 'Por favor ingresa un nombre de anime válido.',
    SERVER_ERROR: 'Error del servidor. Inténtalo más tarde.',
    TIMEOUT_ERROR: 'La búsqueda tardó demasiado. Inténtalo nuevamente.',
  },
  EMPTY_STATES: {
    NO_RESULTS: 'No se encontraron resultados',
    START_SEARCHING: 'Ingresa el nombre de un anime para comenzar',
    NO_ANIME_SELECTED: 'Selecciona un anime para ver recomendaciones',
  }
}

// Configuración de animaciones
export const ANIMATION_CONFIG = {
  DURATION: {
    FAST: 0.2,
    NORMAL: 0.3,
    SLOW: 0.5,
    VERY_SLOW: 0.8,
  },
  EASING: {
    EASE_OUT: 'easeOut',
    EASE_IN: 'easeIn',
    EASE_IN_OUT: 'easeInOut',
    SPRING: 'spring',
  },
  VARIANTS: {
    fadeIn: {
      hidden: { opacity: 0 },
      visible: { opacity: 1 }
    },
    slideUp: {
      hidden: { opacity: 0, y: 30 },
      visible: { opacity: 1, y: 0 }
    },
    slideInLeft: {
      hidden: { opacity: 0, x: -30 },
      visible: { opacity: 1, x: 0 }
    },
    slideInRight: {
      hidden: { opacity: 0, x: 30 },
      visible: { opacity: 1, x: 0 }
    },
    scale: {
      hidden: { opacity: 0, scale: 0.8 },
      visible: { opacity: 1, scale: 1 }
    },
    stagger: {
      visible: {
        transition: {
          staggerChildren: 0.1
        }
      }
    }
  }
}

// Breakpoints para responsive design
export const BREAKPOINTS = {
  XS: '320px',
  SM: '640px',
  MD: '768px',
  LG: '1024px',
  XL: '1280px',
  '2XL': '1536px',
}

// Configuración de colores del tema
export const THEME_COLORS = {
  primary: '#FF6B9D',
  secondary: '#4ECDC4',
  accent: '#FFE66D',
  dark: '#1A1A2E',
  darker: '#16213E',
  light: '#E94560',
  purple: '#9B59B6',
  blue: '#3498DB',
  success: '#27AE60',
  warning: '#F39C12',
  error: '#E74C3C',
  info: '#3498DB',
}

// Configuración de grid y layout
export const LAYOUT_CONFIG = {
  GRID: {
    COLUMNS: {
      MOBILE: 1,
      TABLET: 2,
      DESKTOP: 3,
      LARGE: 4,
    },
    GAP: {
      SMALL: 4,
      MEDIUM: 6,
      LARGE: 8,
    }
  },
  CONTAINER: {
    MAX_WIDTH: '1200px',
    PADDING: {
      MOBILE: '1rem',
      DESKTOP: '2rem',
    }
  }
}

// URLs y endpoints (para futuras extensiones)
export const API_ENDPOINTS = {
  RECOMMENDATIONS: '/recommendations',
  ANIME_LIST: '/animes',
  SEARCH: '/search',
  ANIME_DETAILS: '/anime',
  USER_FAVORITES: '/user/favorites',
  USER_WATCHED: '/user/watched',
}

// Configuración de localStorage keys
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'anime_user_preferences',
  SEARCH_HISTORY: 'anime_search_history',
  FAVORITES: 'anime_favorites',
  WATCHED_LIST: 'anime_watched_list',
  THEME_PREFERENCE: 'anime_theme_preference',
}

// Géneros de anime más comunes (para futuras funcionalidades)
export const ANIME_GENRES = [
  'Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy',
  'Horror', 'Mystery', 'Romance', 'Sci-Fi', 'Slice of Life',
  'Sports', 'Supernatural', 'Thriller', 'Mecha', 'Shounen',
  'Shoujo', 'Seinen', 'Josei', 'Isekai', 'Psychological'
]

// Estados de anime
export const ANIME_STATUS = {
  COMPLETED: 'Completed',
  ONGOING: 'Ongoing',
  UPCOMING: 'Upcoming',
  HIATUS: 'On Hiatus',
  CANCELLED: 'Cancelled',
  UNKNOWN: 'Unknown'
}

export default {
  APP_CONFIG,
  SEARCH_CONFIG,
  RATING_CATEGORIES,
  UI_MESSAGES,
  ANIMATION_CONFIG,
  BREAKPOINTS,
  THEME_COLORS,
  LAYOUT_CONFIG,
  API_ENDPOINTS,
  STORAGE_KEYS,
  ANIME_GENRES,
  ANIME_STATUS,
}