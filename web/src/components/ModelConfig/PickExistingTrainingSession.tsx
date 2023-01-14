import { FC } from 'react'
import { useModelConfigContext } from '../../stores/ModelConfigContext'
import ErrorMessage from '../ErrorMessage'
import LoadingIndicator from '../LoadingIndicator'

interface Props {}

const PickExistingTrainingSession: FC<Props> = () => {
    const {
        selectedSession,
        setSessionId,
        allSessions,
        allSessionsError: error,
        allSessionsLoading: loading,
        fetchAllSessions,
    } = useModelConfigContext()

    return (
        <div className="flex items-center justify-between">
            <div>
                <label htmlFor="model-midi-files" className="text-xl">
                    Choose session
                </label>
                <div className="italic text-gray-400">
                    Choose from the list of all created sessions the one you
                    want to preview
                </div>
            </div>

            {loading && (
                <LoadingIndicator message="Fetching existing sessions" />
            )}
            {error && (
                <ErrorMessage error={error} onRetry={fetchAllSessions}>
                    Failed to fetch existing sessions
                </ErrorMessage>
            )}

            {/* FIXME: pick session */}
        </div>
    )
}

export default PickExistingTrainingSession
