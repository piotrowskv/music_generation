import clsx from 'clsx'
import { HashRouter, Navigate, Route, Routes } from 'react-router-dom'
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
                    <h1 className="text-3xl font-bold">Music generation</h1>
                    <MusicNote className="h-9 w-9 dark:fill-white" />
                    <div className="flex-1"></div>

                    <ThemeSwitch />
                </div>
                <HashRouter>
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
                </HashRouter>
                <div className="flex justify-end">
                    <Credits />
                </div>
            </div>
        </div>
    )
}

export default App
