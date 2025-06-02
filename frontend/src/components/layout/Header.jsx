import React from 'react'
import { Link } from 'react-router-dom'

const Header = () => (
  // <header className="w-full py-8 bg-gradient-to-r from-pink-600 to-purple-700 shadow-md z-20">
  <header className="w-full py-8 bg-gradient-to-r from-purple-700 to-pink-600 shadow-md z-20">
    <div className="max-w-7xl mx-auto flex items-center justify-between px-4">
      <Link to="/" className="text-2xl font-extrabold text-white drop-shadow anime-gradient-text">
        Anime Recommender
      </Link>
      {/* <span className="text-white/80 text-sm font-medium">by Raul</span> */}
      <div className="flex flex-col items-end ml-4">
        <span className="text-white/60 text-xs">Datos de anime de <a href="https://myanimelist.net/" target="_blank" rel="noopener noreferrer" className="underline hover:text-cyan-300 transition">MyAnimeList</a></span>
        <span className="text-white/40 text-xs">Dataset obtenido de <a href="https://www.kaggle.com/datasets/CooperUnion/anime-recommendations-database" target="_blank" rel="noopener noreferrer" className="underline hover:text-cyan-300 transition">Kaggle</a></span>
      </div>
    </div>
  </header>
)

export default Header
