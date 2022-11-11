import { FC, useEffect } from 'react'
import { useModelConfigContext } from '../../stores/ModelConfigContext'
import ErrorMessage from '../ErrorMessage'
import LoadingIndicator from '../LoadingIndicator'
import StepCard from '../StepCard'
import PickModel from './PickModel'
import PickTraining from './PickTraining'

const ModelConfig: FC = () => {
    const {
        pickModel,
        selectedModel,
        init,
        loading,
        error,
        models,
        modelTraining,
        setModelTraining,
    } = useModelConfigContext()

    useEffect(() => {
        init()
    }, [])

    return (
        <div className="flex flex-1 flex-col items-center justify-center gap-4 px-2 py-4 sm:px-24 md:px-36">
            {loading && <LoadingIndicator />}
            {models && (
                <>
                    <StepCard completed={selectedModel !== undefined}>
                        <PickModel
                            models={models.variants}
                            onChange={pickModel}
                            selectedModel={selectedModel}
                        />
                    </StepCard>
                    {selectedModel && (
                        <StepCard completed={modelTraining !== undefined}>
                            <PickTraining
                                modelTraining={modelTraining}
                                onChange={setModelTraining}
                            />
                        </StepCard>
                    )}
                </>
            )}
            {error && (
                <ErrorMessage error={error} onRetry={init}>
                    Failed to fetch model configurations. Is the backend
                    running?
                </ErrorMessage>
            )}
        </div>
    )
}

export default ModelConfig
