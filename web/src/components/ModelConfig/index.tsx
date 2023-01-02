import { FC, useEffect } from 'react'
import {
    ModelTraining,
    useModelConfigContext,
} from '../../stores/ModelConfigContext'
import Button from '../Button'
import ErrorMessage from '../ErrorMessage'
import LoadingIndicator from '../LoadingIndicator'
import StepCard from '../StepCard'
import PickModel from './PickModel'
import PickTraining from './PickTraining'
import UploadFiles, { midiMimeType } from './UploadFiles'

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
    } = useModelConfigContext()

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
                                    files.filter(e => e.type === midiMimeType)
                                )
                            }
                        >
                            <UploadFiles
                                files={midiFiles}
                                onChange={setMidiFiles}
                            />
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
