import axios from 'axios'

/**
 * Configuración base de Axios para la comunicación con la API
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Crear instancia de axios con configuración base
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000, // 10 segundos de timeout
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// Interceptor para requests - agregar logs en desarrollo
api.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    }
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// Interceptor para responses - manejo centralizado de errores
api.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    }
    return response
  },
  (error) => {
    // Manejo centralizado de errores
    const errorMessage = getErrorMessage(error)
    
    if (import.meta.env.DEV) {
      console.error('❌ API Error:', errorMessage)
    }
    
    // Agregar información adicional al error
    error.userMessage = errorMessage
    return Promise.reject(error)
  }
)

/**
 * Extrae un mensaje de error legible para el usuario
 * @param {Error} error - Error de axios
 * @returns {string} Mensaje de error formateado
 */
const getErrorMessage = (error) => {
  if (error.response) {
    // Error de respuesta del servidor
    const status = error.response.status
    const data = error.response.data
    
    switch (status) {
      case 400:
        return data?.detail || 'Solicitud inválida. Verifica los datos enviados.'
      case 404:
        return 'El anime solicitado no fue encontrado.'
      case 422:
        return data?.detail?.[0]?.msg || 'Error de validación en los datos.'
      case 500:
        return 'Error interno del servidor. Inténtalo más tarde.'
      default:
        return data?.detail || `Error del servidor (${status})`
    }
  } else if (error.request) {
    // Error de red/conexión
    return 'No se pudo conectar con el servidor. Verifica tu conexión a internet.'
  } else {
    // Error de configuración
    return 'Error inesperado. Inténtalo nuevamente.'
  }
}

/**
 * Métodos auxiliares para diferentes tipos de requests
 */
export const apiMethods = {
  get: (url, config = {}) => api.get(url, config),
  post: (url, data = {}, config = {}) => api.post(url, data, config),
  put: (url, data = {}, config = {}) => api.put(url, data, config),
  delete: (url, config = {}) => api.delete(url, config),
  patch: (url, data = {}, config = {}) => api.patch(url, data, config),
}

export default api