import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AnimeSearch from '../components/anime/AnimeSearch'
import Button from '../components/common/Button'

const cantidadOpciones = [3, 5, 10, 15, 20, 30, 50]

function Home() {
  const [animeName, setAnimeName] = useState('')
  const [topN, setTopN] = useState(10)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!animeName.trim()) {
      setError('Por favor ingresa el nombre de un anime.')
      return
    }
    setError('')
    navigate(`/recommendations/${encodeURIComponent(animeName.trim())}?topN=${topN}`)
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh]">
      <h1 className="text-4xl font-extrabold text-pink-600 mb-4 drop-shadow-lg">Recomendador de Anime</h1>
      <p className="mb-8 text-lg text-gray-300 max-w-xl text-center">Ingresa el nombre de un anime y elige cuántas recomendaciones quieres recibir. ¡Descubre nuevas historias que te encantarán!</p>
      <form onSubmit={handleSubmit} className="bg-white/10 p-8 rounded-xl shadow-xl flex flex-col gap-6 w-full max-w-md">
        <AnimeSearch value={animeName} onChange={setAnimeName} />
        <div className="flex flex-col gap-2">
          <label htmlFor="topN" className="font-semibold text-gray-200">Cantidad de recomendaciones</label>
          <select
            id="topN"
            value={topN}
            onChange={e => setTopN(Number(e.target.value))}
            className="rounded-lg px-3 py-2 bg-white/80 text-gray-800 focus:outline-pink-500"
          >
            {cantidadOpciones.map(n => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </div>
        {error && <div className="text-red-400 font-semibold text-sm">{error}</div>}
        <Button type="submit" className="mt-2">Buscar recomendaciones</Button>
      </form>
    </div>
  )
}

export default Home
