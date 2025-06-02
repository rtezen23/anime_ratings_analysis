import React from 'react'
import { Link } from 'react-router-dom'

const Header = () => (
  <header className="w-full py-4 bg-gradient-to-r from-pink-600 to-purple-700 shadow-md z-20">
    <div className="max-w-7xl mx-auto flex items-center justify-between px-4">
      <Link to="/" className="text-2xl font-extrabold text-white drop-shadow anime-gradient-text">
        Anime Recommender
      </Link>
      <span className="text-white/80 text-sm font-medium">by Pancho</span>
    </div>
  </header>
)

export default Header
