import React from 'react'

const ErrorMessage = ({ message, className = '' }) => (
  <div className={`bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative max-w-lg mx-auto text-center shadow ${className}`} role="alert">
    <span className="block sm:inline font-semibold">{message}</span>
  </div>
)

export default ErrorMessage
