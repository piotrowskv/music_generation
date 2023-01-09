import { createContext, FC, ReactNode, useContext, useState } from 'react'
import { useParams } from 'react-router-dom'
import { PathParamsFor } from 'ts-routes'
import { apiClient } from '../api'
import {
    ChartPoint,
    TrainingProgress,
    TrainingSession,
} from '../api/dto/models'
import { routes } from '../routes'
import { useAsync } from '../utils/useAsync'

const TrainingSessionContext = createContext<{
    xLabel: string
    yLabel: string
    legends: string[]
    dataPoints: ChartPoint[][]
    trainingFinished: boolean
    // returns dispose callback
    init: () => () => void
    initialLoading: boolean
    initialError: {} | undefined
    trainingSession: TrainingSession | undefined
}>(null!)

export const TrainingSessionProvider: FC<{ children: ReactNode }> = ({
    children,
}) => {
    const { sessionId } =
        useParams<PathParamsFor<typeof routes.trainingSession>>()
    const [trainingData, setTrainingData] = useState<TrainingProgress>({
        finished: false,
        x_label: '',
        y_label: '',
        legends: [],
        chart_series_points: [],
    })

    const {
        loading: initialLoading,
        call: getTrainingSession,
        result: trainingSession,
        error: initialError,
    } = useAsync(apiClient.getTrainingSession)

    function init() {
        const id = sessionId!

        getTrainingSession(id)

        return apiClient.trainingProgress(id, msg =>
            setTrainingData(state => ({
                finished: msg.finished,
                x_label: msg.x_label,
                y_label: msg.y_label,
                legends: msg.legends,
                chart_series_points: [
                    ...state.chart_series_points,
                    ...msg.chart_series_points,
                ],
            }))
        )
    }

    return (
        <TrainingSessionContext.Provider
            value={{
                xLabel: trainingData.x_label,
                yLabel: trainingData.y_label,
                legends: trainingData.legends,
                dataPoints: trainingData.chart_series_points,
                trainingFinished: trainingData.finished,
                init,
                initialLoading,
                initialError,
                trainingSession,
            }}
        >
            {children}
        </TrainingSessionContext.Provider>
    )
}

export const useTrainingSessionContext = () =>
    useContext(TrainingSessionContext)
