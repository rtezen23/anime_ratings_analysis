import React from 'react'
import AnimeCard from './AnimeCard'

function AnimeGrid({ animes }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-7 w-full max-w-6xl mx-auto mt-6">
      {animes.map(anime => (
        <AnimeCard key={anime.id} anime={anime} />
      ))}
    </div>
  )
}

export default AnimeGrid
