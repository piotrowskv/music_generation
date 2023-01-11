export type ModelVariants = {
    variants: ModelVariant[]
}

export type ModelVariant = {
    id: string
    name: string
    description: string
}

export type TrainingSessionCreated = {
    session_id: string
}

export type ChartPoint = {
    x: number
    y: number
}

export type TrainingProgress = {
    finished: boolean
    x_label: string
    y_label: string
    legends: string[]
    chart_series_points: ChartPoint[][]
}

export type TrainingSession = {
    session_id: string
    model: ModelVariant
    created_at: string
    training_file_names: string[]
}
