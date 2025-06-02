import React from 'react'

const Button = ({ children, className = '', ...props }) => (
  <button
    className={`px-5 py-2 rounded-lg font-semibold bg-pink-600 hover:bg-pink-700 text-white shadow transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-pink-400 ${className}`}
    {...props}
  >
    {children}
  </button>
)

export default Button
