import { useState, useEffect } from 'react'

/**
 * Hook personalizado para implementar debounce
 * Útil para optimizar búsquedas en tiempo real y evitar llamadas excesivas a la API
 * 
 * @param {any} value - Valor a debounce
 * @param {number} delay - Retraso en milisegundos (default: 500ms)
 * @returns {any} Valor debounced
 */
export const useDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    // Crear un timeout que actualice el valor debounced después del delay
    const timeoutId = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    // Cleanup: cancelar el timeout si el value cambia antes de que se ejecute
    return () => {
      clearTimeout(timeoutId)
    }
  }, [value, delay])

  return debouncedValue
}

/**
 * Hook más avanzado para debounce con control adicional
 * Proporciona más información sobre el estado del debounce
 * 
 * @param {any} value - Valor a debounce
 * @param {number} delay - Retraso en milisegundos
 * @returns {Object} Objeto con valor debounced y estados adicionales
 */
export const useAdvancedDebounce = (value, delay = 500) => {
  const [debouncedValue, setDebouncedValue] = useState(value)
  const [isPending, setIsPending] = useState(false)

  useEffect(() => {
    // Si el valor es diferente al debounced, marcar como pending
    if (value !== debouncedValue) {
      setIsPending(true)
    }

    const timeoutId = setTimeout(() => {
      setDebouncedValue(value)
      setIsPending(false)
    }, delay)

    return () => {
      clearTimeout(timeoutId)
    }
  }, [value, delay, debouncedValue])

  // Función para cancelar el debounce manualmente
  const cancel = () => {
    setDebouncedValue(value)
    setIsPending(false)
  }

  // Función para forzar la actualización inmediata
  const flush = () => {
    setDebouncedValue(value)
    setIsPending(false)
  }

  return {
    value: debouncedValue,
    isPending,
    cancel,
    flush,
    isDebouncing: isPending
  }
}

/**
 * Hook para debounce de funciones (callback debounce)
 * Útil para debounce de funciones que no dependen de un valor específico
 * 
 * @param {Function} callback - Función a debounce
 * @param {number} delay - Retraso en milisegundos
 * @param {Array} deps - Dependencias del callback
 * @returns {Function} Función debounced
 */
export const useDebounceCallback = (callback, delay = 500, deps = []) => {
  const [timeoutId, setTimeoutId] = useState(null)

  useEffect(() => {
    // Limpiar timeout anterior si las dependencias cambian
    if (timeoutId) {
      clearTimeout(timeoutId)
      setTimeoutId(null)
    }
  }, deps)

  const debouncedCallback = (...args) => {
    // Limpiar timeout anterior
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    // Crear nuevo timeout
    const newTimeoutId = setTimeout(() => {
      callback(...args)
      setTimeoutId(null)
    }, delay)

    setTimeoutId(newTimeoutId)
  }

  // Cleanup al desmontar el componente
  useEffect(() => {
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    }
  }, [timeoutId])

  return debouncedCallback
}

export default useDebounce