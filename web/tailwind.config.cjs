const colors = require('tailwindcss/colors')

/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
    theme: {
        colors: {
            sky: colors.sky,
            white: colors.white,
            gray: '#9ca3af',
            red: colors.rose,
            black: '#292929',
        },
        extend: {
            animation: {
                'spin-once': 'spin 0.5s reverse cubic-bezier(0.32, 0, 0.67, 0)',
            },
            keyframes: {
                wiggle: {
                    '0%, 100%': { transform: 'rotate(-1deg)' },
                    '50%': { transform: 'rotate(1deg)' },
                },
                'wiggle-xl': {
                    '0%, 100%': { transform: 'rotate(-5deg)' },
                    '50%': { transform: 'rotate(5deg)' },
                },
            },
            blur: {
                xs: '1px',
            },
        },
    },
    plugins: [],
    darkMode: 'class',
}
