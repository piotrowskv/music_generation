import clsx from 'clsx'
import { FC } from 'react'
import { useModelConfigContext } from '../../stores/ModelConfigContext'
import ErrorMessage from '../ErrorMessage'
import LoadingIndicator from '../LoadingIndicator'
import './PickExistingTrainingSession.css'

type Props = {}

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
                <div className="italic text-gray">
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
            {allSessions && (
                <table className="fixed-table-head m-4">
                    <thead>
                        <tr>
                            <th>Creation date</th>
                            <th>File count</th>
                            <th>Completed training</th>
                        </tr>
                    </thead>
                    <tbody>
                        {allSessions.map(e => (
                            <tr
                                className={clsx(
                                    'cursor-pointer transition-none hover:bg-gray',
                                    e.session_id ===
                                        selectedSession?.session_id && 'bg-gray'
                                )}
                                key={e.session_id}
                                onClick={() => setSessionId(e.session_id)}
                            >
                                <td>
                                    {new Date(e.created_at).toLocaleString()}
                                </td>
                                <td>{e.file_count}</td>
                                <td>{e.training_completed ? 'yes' : 'no'}</td>
                            </tr>
                        ))}
                        {allSessions.length === 0 && (
                            <tr>
                                <td colSpan={3} className="text-center">
                                    No previously trained models
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            )}
        </div>
    )
}

export default PickExistingTrainingSession
