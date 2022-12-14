import clsx from 'clsx'
import { Link, Navigate, Route, Routes } from 'react-router-dom'
import MusicNote from './assets/MusicNote'
import Credits from './components/Credits'
import ModelConfig from './components/ModelConfig'
import ThemeSwitch from './components/ThemeSwitch'
import TrainingSession from './components/TrainingSession'
import { routes } from './routes'
import { ModelConfigProvider } from './stores/ModelConfigContext'
import { ResolvedTheme, useThemeContext } from './stores/ThemeContext'
import { TrainingSessionProvider } from './stores/TrainingSessionContext'

function App() {
    const { mode } = useThemeContext()

    return (
        <div className={clsx(mode === ResolvedTheme.dark && 'dark')}>
            <div className="min-w-screen flex min-h-screen flex-col bg-white p-4 text-black dark:bg-black dark:text-white">
                <div className="flex">
                    <Link className="text-3xl font-bold" to={routes.root()}>
                        Music generation
                    </Link>
                    <MusicNote className="h-9 w-9 hover:animate-[wiggle-xl_0.7s_ease-in-out_infinite] dark:fill-white" />
                    <div className="flex-1"></div>

                    <ThemeSwitch />
                </div>
                <Routes>
                    <Route
                        path={routes.root.pattern}
                        element={
                            <ModelConfigProvider>
                                <ModelConfig />
                            </ModelConfigProvider>
                        }
                    />
                    <Route
                        path={routes.trainingSession.pattern}
                        element={
                            <TrainingSessionProvider>
                                <TrainingSession />
                            </TrainingSessionProvider>
                        }
                    />
                    <Route
                        path="*"
                        element={<Navigate to={routes.root()} replace />}
                    />
                </Routes>
                <div className="flex justify-end">
                    <Credits />
                </div>
            </div>
        </div>
    )
}

export default App
