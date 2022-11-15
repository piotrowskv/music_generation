import { createContext, FC, ReactNode, useContext, useState } from 'react'
import { apiClient } from '../api'
import { ModelVariant, ModelVariants } from '../api/dto/models'
import { useAsync } from '../utils/useAsync'

export enum ModelTraining {
    pretrained,
    trainMyself,
}

const ModelConfigContext = createContext<{
    init: () => void
    selectedModel: ModelVariant | undefined
    pickModel: (id: string | undefined) => void
    modelTraining: ModelTraining | undefined
    setModelTraining: (id: ModelTraining | undefined) => void
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
    const [modelTraining, setModelTraining] = useState<
        ModelTraining | undefined
    >(undefined)

    return (
        <ModelConfigContext.Provider
            value={{
                selectedModel: models?.variants.find(
                    e => e.id === chosenModelId
                ),
                pickModel: setChosenModelId,
                modelTraining,
                setModelTraining,
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
