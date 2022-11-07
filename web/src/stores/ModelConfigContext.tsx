import { createContext, FC, ReactNode, useContext, useState } from 'react'
import { apiClient } from '../api'
import { ModelVariant, ModelVariants } from '../api/models/models'
import { useAsync } from '../utils/useAsync'

const ModelConfigContext = createContext<{
    selectedModel: ModelVariant | undefined
    // setting undefined removes selection
    pickModel: (id: string | undefined) => void
    init: () => void
    models: ModelVariants | undefined
    loading: boolean
    error: {} | undefined
}>(null!)

export const ModelConfigProvider: FC<{ children: ReactNode }> = ({
    children,
}) => {
    const {
        loading,
        call: init,
        result: models,
        error,
    } = useAsync(apiClient.getModelVariants)

    const [chosenModelId, setChosenModelId] = useState<string | undefined>(
        undefined
    )

    return (
        <ModelConfigContext.Provider
            value={{
                selectedModel: models?.variants.find(
                    e => e.id === chosenModelId
                ),
                pickModel: setChosenModelId,
                loading,
                error,
                models,
                init,
            }}
        >
            {children}
        </ModelConfigContext.Provider>
    )
}

export const useModelConfigContext = () => useContext(ModelConfigContext)
