import {
    createContext,
    FC,
    ReactNode,
    useContext,
    useEffect,
    useState,
} from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../api'
import { ModelVariant, ModelVariants } from '../api/dto/models'
import { routes } from '../routes'
import { useAsync } from '../utils/useAsync'

export enum ModelTraining {
    pretrained,
    trainMyself,
}

const ModelConfigContext = createContext<{
    init: () => void
    registerTrainingSession: (modelId: string, files: File[]) => void
    selectedModel: ModelVariant | undefined
    pickModel: (id: string | undefined) => void
    modelTraining: ModelTraining | undefined
    setModelTraining: (id: ModelTraining | undefined) => void
    midiFiles: File[]
    setMidiFiles: (files: File[]) => void
    models: ModelVariants | undefined
    initialLoading: boolean
    initialError: {} | undefined
    sessionRegisterLoading: boolean
    sessionRegisterError: {} | undefined
}>(null!)

export const ModelConfigProvider: FC<{ children: ReactNode }> = ({
    children,
}) => {
    const {
        loading: initialLoading,
        call: init,
        result: models,
        error: initialError,
    } = useAsync(apiClient.getModelVariants)
    const {
        loading: sessionRegisterLoading,
        call: registerTrainingSession,
        result: trainingSessionToken,
        error: sessionRegisterError,
    } = useAsync(apiClient.registerTraining)

    const [chosenModelId, setChosenModelId] = useState<string | undefined>(
        undefined
    )
    const [modelTraining, setModelTraining] = useState<
        ModelTraining | undefined
    >(undefined)
    const [midiFiles, setMidiFiles] = useState<File[]>([])
    const navigate = useNavigate()

    useEffect(() => {
        const token = trainingSessionToken?.token
        if (token) {
            // we got a training token, navigate to the session automatically
            navigate(routes.trainingSession({ sessionToken: token }))
        }
    }, [trainingSessionToken])

    return (
        <ModelConfigContext.Provider
            value={{
                selectedModel: models?.variants.find(
                    e => e.id === chosenModelId
                ),
                pickModel: setChosenModelId,
                modelTraining,
                setModelTraining,
                midiFiles,
                setMidiFiles,
                initialLoading,
                initialError,
                sessionRegisterLoading,
                sessionRegisterError,
                registerTrainingSession,
                models,
                init,
            }}
        >
            {children}
        </ModelConfigContext.Provider>
    )
}

export const useModelConfigContext = () => useContext(ModelConfigContext)
