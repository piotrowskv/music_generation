const colors = require('tailwindcss/colors')

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    theme: {
        colors: {
            ...colors,
            black: '#292929',
        },
        extend: {},
    },
    plugins: [],
    darkMode: 'class',
}
