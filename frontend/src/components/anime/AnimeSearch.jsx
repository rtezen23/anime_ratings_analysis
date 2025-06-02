import React from 'react'

function AnimeSearch({ value, onChange }) {
  return (
    <div className="flex flex-col gap-2">
      <label htmlFor="animeName" className="font-semibold text-gray-200">Nombre del anime</label>
      <input
        id="animeName"
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder="Ej: Naruto, One Piece, Death Note..."
        className="rounded-lg px-3 py-2 bg-white/80 text-gray-800 focus:outline-pink-500"
        autoComplete="off"
        required
      />
    </div>
  )
}

export default AnimeSearch
