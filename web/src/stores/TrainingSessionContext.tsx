import {
    createContext,
    FC,
    ReactNode,
    useContext,
    useEffect,
    useState,
} from 'react'
import { useParams } from 'react-router-dom'
import { PathParamsFor } from 'ts-routes'
import { apiClient } from '../api'
import { ChartPoint, ChartSeries, TrainingProgress } from '../api/dto/models'
import { routes } from '../routes'

const TrainingSessionContext = createContext<{
    xLabel: string
    yLabel: string
    legends: string[]
    dataPoints: ChartPoint[][]
}>(null!)

export const TrainingSessionProvider: FC<{ children: ReactNode }> = ({
    children,
}) => {
    const [trainingData, setTrainingData] = useState<TrainingProgress>({
        finished: false,
        x_label: '',
        y_label: '',
        chart_series: [],
    })
    const { sessionId } =
        useParams<PathParamsFor<typeof routes.trainingSession>>()

    useEffect(() => {
        return apiClient.trainingProgress(sessionId!, msg =>
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
    }, [])

    const dataPoints = transformChartSeries(trainingData.chart_series)

    return (
        <TrainingSessionContext.Provider
            value={{
                xLabel: trainingData.x_label,
                yLabel: trainingData.y_label,
                legends: trainingData.chart_series.map(e => e.legend),
                dataPoints,
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
