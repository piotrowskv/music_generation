import { createContext, FC, ReactNode, useContext, useState } from 'react'

const ModelConfigContext = createContext<{
    chosenModelId: string | undefined
    // setting undefined removes selection
    pickModel: (id: string | undefined) => void
}>(null!)

export const ModelConfigProvider: FC<{ children: ReactNode }> = ({
    children,
}) => {
    const [chosenModel, setChosenModel] = useState<string | undefined>(
        undefined
    )

    return (
        <ModelConfigContext.Provider
            value={{ chosenModelId: chosenModel, pickModel: setChosenModel }}
        >
            {children}
        </ModelConfigContext.Provider>
    )
}

export const useModelConfigContext = () => useContext(ModelConfigContext)
