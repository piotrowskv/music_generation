import { FC, useEffect } from 'react'
import { useModelConfigContext } from '../../stores/ModelConfigContext'
import ErrorMessage from '../ErrorMessage'
import LoadingIndicator from '../LoadingIndicator'
import StepCard from '../StepCard'
import PickModel from './PickModel'

const ModelConfig: FC = () => {
    const { pickModel, selectedModel, init, loading, error, models } =
        useModelConfigContext()

    useEffect(() => {
        init()
    }, [])

    return (
        <div className="flex flex-1 items-center justify-center px-2 py-4 sm:px-24 md:px-36">
            {loading && <LoadingIndicator />}
            {models && (
                <StepCard completed={false}>
                    <PickModel
                        models={models.variants}
                        onChangePickedModel={pickModel}
                        selectedModel={selectedModel}
                    />
                </StepCard>
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
