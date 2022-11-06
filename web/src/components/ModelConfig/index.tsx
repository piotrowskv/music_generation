import { FC, useEffect } from 'react'
import { apiClient } from '../../api'
import { useAsync } from '../../utils/useAsync'
import ErrorMessage from '../ErrorMessage'
import LoadingIndicator from '../LoadingIndicator'
import StepCard from '../StepCard'
import PickModel from './PickModel'

const ModelConfig: FC = () => {
    const {
        loading,
        call: fetchModelConfig,
        result: config,
        error,
    } = useAsync(apiClient.getModelVariants)

    useEffect(() => {
        fetchModelConfig()
    }, [])

    return (
        <div className="flex flex-1 items-center justify-center px-2 py-4 sm:px-24 md:px-36">
            {loading && <LoadingIndicator />}
            {config && (
                <StepCard completed={false}>
                    <PickModel models={config.variants} />
                </StepCard>
            )}
            {error && (
                <ErrorMessage error={error} onRetry={fetchModelConfig}>
                    Failed to fetch model configurations. Is the backend
                    running?
                </ErrorMessage>
            )}
        </div>
    )
}

export default ModelConfig
