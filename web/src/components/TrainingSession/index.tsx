import { FC } from 'react'
import { useParams } from 'react-router-dom'
import { PathParamsFor } from 'ts-routes'
import { routes } from '../../routes'
import { useTrainingSessionContext } from '../../stores/TrainingSessionContext'

const TrainingSession: FC = () => {
    const { sessionToken } =
        useParams<PathParamsFor<typeof routes.trainingSession>>()

    const {} = useTrainingSessionContext()

    return (
        <div className="flex flex-1 flex-col items-center justify-center gap-4 px-2 py-4 sm:px-24 md:px-36">
            welcome in session {sessionToken}
        </div>
    )
}

export default TrainingSession
