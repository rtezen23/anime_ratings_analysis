import React from 'react'

const ratingColors = {
  excellent: 'bg-green-400',
  high: 'bg-blue-400',
  medium: 'bg-yellow-400',
  low: 'bg-red-400',
}

function RatingDisplay({ rating, category }) {
  const percent = Math.round((rating / 10) * 100)
  return (
    <div className="flex items-center gap-2">
      <div className="w-24 h-3 bg-white/20 rounded-full overflow-hidden">
        <div
          className={`h-full ${ratingColors[category] || 'bg-gray-400'}`}
          style={{ width: `${percent}%` }}
        />
      </div>
      <span className={`font-bold ${category === 'excellent' ? 'text-green-300' : category === 'high' ? 'text-blue-200' : category === 'medium' ? 'text-yellow-200' : 'text-red-200'}`}>{rating}</span>
    </div>
  )
}

export default RatingDisplay
