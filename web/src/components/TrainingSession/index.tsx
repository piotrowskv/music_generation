import { FC, useEffect } from 'react'
import { useTrainingSessionContext } from '../../stores/TrainingSessionContext'
import ErrorMessage from '../ErrorMessage'
import LoadingIndicator from '../LoadingIndicator'
import TrainingChart from './TrainingChart'

const TrainingSession: FC = () => {
    const { init, initialLoading, trainingSession, initialError } =
        useTrainingSessionContext()

    useEffect(() => init(), [])

    return (
        <div className="flex flex-1 flex-col items-center justify-center gap-4 px-2 py-4 sm:px-24 md:px-36">
            {initialLoading && (
                <LoadingIndicator message="Fetching training session" />
            )}
            {trainingSession && (
                <TrainingChart trainingSession={trainingSession} />
            )}
            {initialError && (
                <ErrorMessage error={initialError} onRetry={init}>
                    Failed to fetch training session.
                </ErrorMessage>
            )}
        </div>
    )
}

export default TrainingSession
