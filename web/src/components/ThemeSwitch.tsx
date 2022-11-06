import React from 'react'
import Moon from '../assets/Moon'
import Sun from '../assets/Sun'
import {
    ResolvedTheme,
    ThemeMode,
    useThemeContext,
} from '../stores/ThemeContext'

interface Props {}

const ThemeSwitch: React.FC<Props> = ({}) => {
    const { mode, changeMode } = useThemeContext()

    let Icon = mode === ResolvedTheme.dark ? Moon : Sun

    return (
        <button
            className="h-9 w-9"
            onClick={() =>
                changeMode(
                    mode === ResolvedTheme.dark
                        ? ThemeMode.light
                        : ThemeMode.dark
                )
            }
        >
            <Icon className="h-9 w-9 hover:fill-gray-500 dark:fill-white hover:dark:fill-gray-500" />
        </button>
    )
}

export default ThemeSwitch
