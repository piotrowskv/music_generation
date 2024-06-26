import { FC, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { routes } from '../../routes'
import {
    ModelTraining,
    useModelConfigContext,
} from '../../stores/ModelConfigContext'
import Button from '../Button'
import ErrorMessage from '../ErrorMessage'
import LoadingIndicator from '../LoadingIndicator'
import StepCard from '../StepCard'
import PickExistingTrainingSession from './PickExistingTrainingSession'
import PickModel from './PickModel'
import PickTraining from './PickTraining'
import UploadFiles, { midiMimeTypes } from './UploadFiles'

const ModelConfig: FC = () => {
    const {
        pickModel,
        selectedModel,
        init,
        initialLoading,
        initialError,
        models,
        modelTraining,
        setModelTraining,
        midiFiles,
        setMidiFiles,
        sessionRegisterLoading,
        registerTrainingSession,
        sessionRegisterError,
        selectedSession,
    } = useModelConfigContext()
    const navigate = useNavigate()

    useEffect(() => {
        init()
    }, [])

    const createTrainingSession = () => {
        registerTrainingSession(selectedModel!.id, midiFiles)
    }

    return (
        <div className="flex flex-1 flex-col items-center justify-center gap-4 px-2 py-4 sm:px-24 md:px-36">
            {initialLoading && (
                <LoadingIndicator message="Fetching available models" />
            )}
            {models && (
                <>
                    <StepCard
                        completed={selectedModel !== undefined}
                        disabled={sessionRegisterLoading}
                    >
                        <PickModel
                            models={models.variants}
                            onChange={pickModel}
                            selectedModel={selectedModel}
                        />
                    </StepCard>
                    {selectedModel && (
                        <StepCard
                            completed={modelTraining !== undefined}
                            disabled={sessionRegisterLoading}
                        >
                            <PickTraining
                                modelTraining={modelTraining}
                                onChange={setModelTraining}
                            />
                        </StepCard>
                    )}
                    {modelTraining === ModelTraining.trainMyself && (
                        <StepCard
                            completed={midiFiles.length > 0}
                            disabled={sessionRegisterLoading}
                            onDrop={files =>
                                setMidiFiles(
                                    files.filter(e => midiMimeTypes.has(e.type))
                                )
                            }
                        >
                            <UploadFiles
                                files={midiFiles}
                                onChange={setMidiFiles}
                            />
                        </StepCard>
                    )}
                    {modelTraining === ModelTraining.pretrained && (
                        <StepCard
                            completed={selectedSession !== undefined}
                            disabled={false}
                        >
                            <PickExistingTrainingSession />
                        </StepCard>
                    )}
                    {midiFiles.length > 0 &&
                        modelTraining === ModelTraining.trainMyself && (
                            <>
                                <Button
                                    onClick={
                                        sessionRegisterLoading
                                            ? () => {
                                                  // do nothing
                                              }
                                            : createTrainingSession
                                    }
                                >
                                    {sessionRegisterLoading ? (
                                        <LoadingIndicator message="Creating training session..." />
                                    ) : (
                                        'Start training'
                                    )}
                                </Button>
                                {sessionRegisterError && (
                                    <ErrorMessage error={sessionRegisterError}>
                                        Failed to create a new training session.
                                    </ErrorMessage>
                                )}
                            </>
                        )}
                    {selectedSession !== undefined &&
                        modelTraining === ModelTraining.pretrained && (
                            <>
                                <Button
                                    onClick={() =>
                                        navigate(
                                            routes.trainingSession({
                                                sessionId:
                                                    selectedSession.session_id,
                                            })
                                        )
                                    }
                                >
                                    See session
                                </Button>
                            </>
                        )}
                </>
            )}
            {initialError && (
                <ErrorMessage error={initialError} onRetry={init}>
                    Failed to fetch model configurations. Is the backend
                    running?
                </ErrorMessage>
            )}
        </div>
    )
}

export default ModelConfig
