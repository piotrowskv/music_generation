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
import {
    ModelVariant,
    ModelVariants,
    TrainingSessionSummary,
} from '../api/dto/models'
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
    selectedSession: TrainingSessionSummary | undefined
    setSessionId: (id: string | undefined) => void
    midiFiles: File[]
    setMidiFiles: (files: File[]) => void
    models: ModelVariants | undefined
    initialLoading: boolean
    initialError: {} | undefined
    sessionRegisterLoading: boolean
    sessionRegisterError: {} | undefined
    allSessionsLoading: boolean
    allSessionsError: {} | undefined
    allSessions: TrainingSessionSummary[] | undefined
    fetchAllSessions: () => void
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
        result: trainingSessionId,
        error: sessionRegisterError,
    } = useAsync(apiClient.registerTraining)
    const {
        loading: allSessionsLoading,
        call: fetchAllSessions,
        result: allSessions,
        error: allSessionsError,
    } = useAsync(apiClient.getAllTrainingSessions)

    const [chosenModelId, setChosenModelId] = useState<string | undefined>(
        undefined
    )
    const [modelTraining, setModelTraining] = useState<
        ModelTraining | undefined
    >(undefined)
    const [selectedSessionId, setSelectedSessionId] = useState<
        string | undefined
    >(undefined)
    const [midiFiles, setMidiFiles] = useState<File[]>([])
    const navigate = useNavigate()

    useEffect(() => {
        const sessionId = trainingSessionId?.session_id
        if (sessionId) {
            // we got a training sessionId, navigate to the session automatically
            navigate(routes.trainingSession({ sessionId }))
        }
    }, [trainingSessionId])

    useEffect(() => {
        if (modelTraining === ModelTraining.pretrained && !allSessionsLoading) {
            // pretrained option was selected, fetch all sessions if not doing it already
            fetchAllSessions()
        }
    }, [modelTraining])

    return (
        <ModelConfigContext.Provider
            value={{
                selectedModel: models?.variants.find(
                    e => e.id === chosenModelId
                ),
                pickModel: setChosenModelId,
                selectedSession: allSessions?.sessions.find(
                    e => e.session_id === selectedSessionId
                ),
                setSessionId(id) {
                    if (id) {
                        setMidiFiles([])
                    }
                    setSelectedSessionId(id)
                },
                modelTraining,
                setModelTraining,
                midiFiles,
                setMidiFiles(files) {
                    if (files.length !== 0) {
                        setSelectedSessionId(undefined)
                    }
                    setMidiFiles(files)
                },
                initialLoading,
                initialError,
                sessionRegisterLoading,
                sessionRegisterError,
                registerTrainingSession,
                allSessionsLoading,
                allSessions: allSessions?.sessions,
                allSessionsError,
                fetchAllSessions,
                models,
                init,
            }}
        >
            {children}
        </ModelConfigContext.Provider>
    )
}

export const useModelConfigContext = () => useContext(ModelConfigContext)
