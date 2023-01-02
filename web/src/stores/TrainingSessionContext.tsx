import { createContext, FC, ReactNode, useContext } from 'react'

const TrainingSessionContext = createContext<{}>(null!)

export const TrainingSessionProvider: FC<{ children: ReactNode }> = ({
    children,
}) => {
    return (
        <TrainingSessionContext.Provider value={{}}>
            {children}
        </TrainingSessionContext.Provider>
    )
}

export const useTrainingSessionContext = () =>
    useContext(TrainingSessionContext)
