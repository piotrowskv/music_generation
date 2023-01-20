import { FC, useEffect } from 'react'
import { useTrainingSessionContext } from '../../stores/TrainingSessionContext'
import ErrorMessage from '../ErrorMessage'
import LoadingIndicator from '../LoadingIndicator'
import TrainingChart from './TrainingChart'

const TrainingSession: FC = () => {
    const {
        init,
        initialLoading,
        trainingSession,
        initialError,
        trainingFinished,
        trainingError,
    } = useTrainingSessionContext()

    useEffect(() => init(), [])

    return (
        <div className="flex flex-1 flex-col items-center justify-center gap-4 px-2 py-4 sm:px-24 md:px-36">
            {initialLoading && (
                <LoadingIndicator message="Fetching training session" />
            )}
            {trainingSession && (
                <>
                    <h3 className="text-2xl">
                        {trainingSession.model.name} training on{' '}
                        {trainingSession.training_file_names.length} MIDI files
                    </h3>
                    {trainingError ? (
                        <ErrorMessage error={trainingError}>
                            Failed to train the model:
                        </ErrorMessage>
                    ) : (
                        <div className="italic text-gray">
                            {trainingFinished ? 'Ready!' : 'In progress...'}
                        </div>
                    )}
                    {!trainingError && <TrainingChart />}
                </>
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
