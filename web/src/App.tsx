import clsx from 'clsx'
import MusicNote from './assets/MusicNote'
import Credits from './components/Credits'
import ThemeSwitch from './components/ThemeSwitch'
import { ResolvedTheme, useThemeContext } from './stores/ThemeContext'

function App() {
    const { mode } = useThemeContext()

    return (
        <div className={clsx(mode === ResolvedTheme.dark && 'dark')}>
            <div className="flex h-screen w-screen flex-col bg-white p-4 text-black dark:bg-black dark:text-white">
                <div className="flex">
                    <h1 className="text-3xl font-bold">Music generation</h1>
                    <MusicNote className="h-9 w-9 dark:fill-white" />
                    <div className="flex-1"></div>

                    <ThemeSwitch />
                </div>
                <div className="flex-1"></div>
                <div className="flex justify-end">
                    <Credits />
                </div>
            </div>
        </div>
    )
}

export default App
