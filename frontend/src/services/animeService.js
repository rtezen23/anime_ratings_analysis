import { apiMethods } from './api'

/**
 * Servicio para operaciones relacionadas con anime
 * Centraliza todas las llamadas a la API de recomendaciones
 */
class AnimeService {
  /**
   * Obtiene recomendaciones para un anime específico
   * @param {string} animeName - Nombre del anime
   * @param {number} topN - Número de recomendaciones a obtener (default: 10)
   * @returns {Promise<Object>} Respuesta con las recomendaciones
   */
  async getRecommendations(animeName, topN = 10) {
    try {
      // Validar parámetros de entrada
      if (!animeName || typeof animeName !== 'string' || animeName.trim().length === 0) {
        throw new Error('El nombre del anime es requerido y debe ser válido')
      }

      if (topN < 1 || topN > 50) {
        throw new Error('El número de recomendaciones debe estar entre 1 y 50')
      }

      // Limpiar y codificar el nombre del anime para la URL
      const cleanAnimeName = animeName.trim()
      const encodedAnimeName = encodeURIComponent(cleanAnimeName)
      
      const response = await apiMethods.get(
        `/recommendations/${encodedAnimeName}`,
        {
          params: { top_n: topN }
        }
      )

      // Procesar y validar la respuesta
      const processedData = this.processRecommendationsResponse(response.data, cleanAnimeName)
      return processedData

    } catch (error) {
      console.error('Error getting recommendations:', error)
      throw this.handleServiceError(error, animeName)
    }
  }

  /**
   * Procesa la respuesta de recomendaciones para asegurar formato consistente
   * @param {Object} data - Datos de respuesta de la API
   * @param {string} originalAnime - Nombre original del anime buscado
   * @returns {Object} Datos procesados y validados
   */
  processRecommendationsResponse(data, originalAnime) {
    // Estructura esperada de la respuesta
    const processedData = {
      originalAnime: originalAnime,
      recommendations: [],
      totalRecommendations: 0,
      timestamp: new Date().toISOString(),
    }

    // Verificar si hay recomendaciones
    if (!data || !Array.isArray(data.recommendations)) {
      console.warn('No recommendations found in response:', data)
      return processedData
    }

    // Procesar cada recomendación
    processedData.recommendations = data.recommendations.map((rec, index) => ({
      id: rec.id || index,
      name: rec.anime_name || rec.name || rec.title || 'Título no disponible',
      similarity: this.validateSimilarity(rec.similarity_score),
      rating: this.validateRating(rec.rating),
      genres: Array.isArray(rec.genres) ? rec.genres : [],
      year: rec.year || null,
      episodes: rec.episodes || null,
      status: rec.status || 'Unknown',
      synopsis: rec.synopsis || '',
      imageUrl: rec.image_url || rec.imageUrl || null,
      rank: rec.rank || index + 1,
      // Determinar si es una recomendación destacada (top 3)
      isHighlighted: index < 3,
      // Categoría de rating para estilos visuales
      ratingCategory: this.getRatingCategory(rec.rating),
    }))

    processedData.totalRecommendations = processedData.recommendations.length

    return processedData
  }

  /**
   * Valida y normaliza el valor de similaridad
   * @param {any} similarity - Valor de similaridad
   * @returns {number} Similaridad validada (0-100)
   */
  validateSimilarity(similarity) {
    const sim = parseFloat(similarity)
    if (isNaN(sim)) return 0
    
    // Si está en formato decimal (0-1), convertir a porcentaje
    if (sim <= 1) return Math.round(sim * 100)
    
    // Si ya está en porcentaje, asegurar que esté en rango válido
    return Math.max(0, Math.min(100, Math.round(sim)))
  }

  /**
   * Valida y normaliza el valor de rating
   * @param {any} rating - Valor de rating
   * @returns {number} Rating validado (0-10)
   */
  validateRating(rating) {
    const rat = parseFloat(rating)
    if (isNaN(rat)) return 0
    return Math.max(0, Math.min(10, Math.round(rat * 10) / 10))
  }

  /**
   * Determina la categoría de rating para estilos visuales
   * @param {number} rating - Rating numérico
   * @returns {string} Categoría del rating
   */
  getRatingCategory(rating) {
    const validRating = this.validateRating(rating)
    
    if (validRating >= 8.5) return 'excellent'
    if (validRating >= 7.0) return 'high'
    if (validRating >= 5.0) return 'medium'
    return 'low'
  }

  /**
   * Maneja errores del servicio y los convierte en errores más útiles
   * @param {Error} error - Error original
   * @param {string} animeName - Nombre del anime que causó el error
   * @returns {Error} Error procesado
   */
  handleServiceError(error, animeName) {
    if (error.userMessage) {
      // Error ya procesado por el interceptor de axios
      return new Error(error.userMessage)
    }

    if (error.message) {
      // Error de validación local
      return new Error(error.message)
    }

    // Error genérico
    return new Error(`No se pudieron obtener recomendaciones para "${animeName}". Inténtalo nuevamente.`)
  }

  /**
   * Método para futuras implementaciones - obtener lista de animes
   * @returns {Promise<Array>} Lista de animes disponibles
   */
  async getAnimeList() {
    // TODO: Implementar cuando la API tenga endpoint para lista de animes
    try {
      const response = await apiMethods.get('/animes')
      return response.data
    } catch (error) {
      console.warn('Anime list endpoint not available yet')
      return []
    }
  }

  /**
   * Método para futuras implementaciones - búsqueda de animes
   * @param {string} query - Término de búsqueda
   * @returns {Promise<Array>} Resultados de búsqueda
   */
  async searchAnimes(query) {
    // TODO: Implementar cuando la API tenga endpoint de búsqueda
    try {
      const response = await apiMethods.get('/search', {
        params: { q: query }
      })
      return response.data
    } catch (error) {
      console.warn('Search endpoint not available yet')
      return []
    }
  }

  /**
   * Método para futuras implementaciones - obtener detalles de anime
   * @param {string|number} animeId - ID del anime
   * @returns {Promise<Object>} Detalles del anime
   */
  async getAnimeDetails(animeId) {
    // TODO: Implementar cuando la API tenga endpoint de detalles
    try {
      const response = await apiMethods.get(`/anime/${animeId}`)
      return response.data
    } catch (error) {
      console.warn('Anime details endpoint not available yet')
      return null
    }
  }
}

// Exportar instancia singleton del servicio
const animeService = new AnimeService()
export default animeService