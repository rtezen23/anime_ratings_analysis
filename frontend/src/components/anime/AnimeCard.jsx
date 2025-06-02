import React from 'react'
import RatingDisplay from './RatingDisplay'

function AnimeCard({ anime }) {
  return (
    <div className={`relative rounded-xl shadow-lg p-5 bg-gradient-to-br from-pink-600/80 to-purple-800/80 text-white flex flex-col gap-3 border-2 ${anime.isHighlighted ? 'border-yellow-400 scale-105 z-10' : 'border-transparent'} transition-transform duration-200`}>
      {anime.isHighlighted && (
        <div className="absolute -top-3 -right-3 bg-yellow-400 text-yellow-900 font-bold px-3 py-1 rounded-full shadow-md text-xs animate-bounce">TOP {anime.rank}</div>
      )}
      <div className="flex flex-col gap-1">
        <h3 className="text-xl font-bold drop-shadow mb-1">{anime.name}</h3>
        <div className="flex items-center gap-2">
          <RatingDisplay rating={anime.rating} category={anime.ratingCategory} />
          <span className="text-sm text-gray-200">({anime.rating})</span>
        </div>
        <div className="text-sm text-pink-200">Similaridad: <span className="font-bold text-white">{anime.similarity}%</span></div>
        {anime.genres && anime.genres.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {anime.genres.map(g => (
              <span key={g} className="bg-white/20 text-xs px-2 py-0.5 rounded-full">{g}</span>
            ))}
          </div>
        )}
      </div>
      {anime.year && <div className="text-xs text-gray-300 mt-2">Año: {anime.year}</div>}
      {anime.episodes && <div className="text-xs text-gray-300">Episodios: {anime.episodes}</div>}
      {/* {anime.status && <div className="text-xs text-gray-300">Estado: {anime.status}</div>} */}
    </div>
  )
}

export default AnimeCard
