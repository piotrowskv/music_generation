import { FC } from 'react'
import {
    CartesianGrid,
    Label,
    Legend,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts'
import { useTrainingSessionContext } from '../../stores/TrainingSessionContext'

type Props = {}

const TrainingChart: FC<Props> = () => {
    const { xLabel, yLabel, legends, dataPoints } = useTrainingSessionContext()

    return (
        <ResponsiveContainer width="100%" height={500}>
            <LineChart
                data={dataPoints}
                margin={{
                    top: 20,
                    right: 20,
                    bottom: 20,
                    left: 20,
                }}
            >
                <CartesianGrid strokeDasharray="3 3" />
                <Legend align="right" />
                <Tooltip contentStyle={{ color: '#292929' }} />
                {[...new Array(dataPoints[0]?.length ?? 0)].map((_, i) => (
                    <XAxis dataKey={obj => obj[i].x} key={i} type="number">
                        <Label offset={-2} position="insideBottom">
                            {xLabel}
                        </Label>
                    </XAxis>
                ))}
                <YAxis>
                    <Label
                        angle={270}
                        position="left"
                        offset={-12}
                        style={{ textAnchor: 'middle' }}
                    >
                        {yLabel}
                    </Label>
                </YAxis>
                {[...new Array(dataPoints[0]?.length ?? 0)].map((_, i) => (
                    <Line
                        type="monotone"
                        dataKey={obj => obj[i].y}
                        stroke={getSeriesColor(i)}
                        name={legends[i]}
                        key={i}
                    />
                ))}
            </LineChart>
        </ResponsiveContainer>
    )
}

function getSeriesColor(i: number): string {
    const colors = ['#f5832c', '#94cf1f', '#214eff']

    return colors[i % colors.length]
}

export default TrainingChart
