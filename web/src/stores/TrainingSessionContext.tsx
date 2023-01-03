import { createContext, FC, ReactNode, useContext, useState } from 'react'
import { useParams } from 'react-router-dom'
import { PathParamsFor } from 'ts-routes'
import { apiClient } from '../api'
import {
    ChartPoint,
    ChartSeries,
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
        chart_series: [],
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
                chart_series: msg.chart_series.map((e, i) => ({
                    legend: e.legend,
                    points: [
                        ...(state.chart_series[i]?.points ?? []),
                        ...e.points,
                    ],
                })),
            }))
        )
    }

    const dataPoints = transformChartSeries(trainingData.chart_series)

    return (
        <TrainingSessionContext.Provider
            value={{
                xLabel: trainingData.x_label,
                yLabel: trainingData.y_label,
                legends: trainingData.chart_series.map(e => e.legend),
                dataPoints,
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

function transformChartSeries(series: ChartSeries[]): ChartPoint[][] {
    const dataPoints = []
    const longest = Math.max(...series.map(e => e.points.length))
    for (let i = 0; i < longest; i++) {
        dataPoints.push(series.map(e => e.points[i]))
    }

    return dataPoints
}
