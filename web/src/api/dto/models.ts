export type ModelVariants = {
    variants: ModelVariant[]
}

export type ModelVariant = {
    id: string
    name: string
    description: string
}

export type TrainingSessionCreated = {
    token: string
}
