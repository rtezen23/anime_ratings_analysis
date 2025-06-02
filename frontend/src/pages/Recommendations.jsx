import React, { useEffect, useState } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import animeService from '../services/animeService'
import AnimeGrid from '../components/anime/AnimeGrid'
import LoadingSpinner from '../components/common/LoadingSpinner'
import ErrorMessage from '../components/common/ErrorMessage'
import Button from '../components/common/Button'

function Recommendations() {
  const { animeName } = useParams()
  const [searchParams] = useSearchParams()
  const topN = Number(searchParams.get('topN')) || 10
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    setLoading(true)
    setError('')
    animeService.getRecommendations(animeName, topN)
      .then(setData)
      .catch(err => setError(err.message || 'Error al obtener recomendaciones'))
      .finally(() => setLoading(false))
  }, [animeName, topN])

  return (
    <div className="flex flex-col items-center min-h-[70vh] py-8">
      <h2 className="text-3xl font-bold text-pink-500 mb-2 drop-shadow">Recomendaciones para: <span className="text-white">{decodeURIComponent(animeName)}</span></h2>
      <p className="mb-6 text-gray-300">Top {topN} recomendaciones similares</p>
      <Button onClick={() => navigate('/')} className="mb-6">Volver a buscar</Button>
      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {data && data.recommendations && data.recommendations.length > 0 && (
        <AnimeGrid animes={data.recommendations} />
      )}
      {data && data.recommendations && data.recommendations.length === 0 && !loading && !error && (
        <div className="text-gray-400 mt-8">No se encontraron recomendaciones para este anime.</div>
      )}
    </div>
  )
}

export default Recommendations
