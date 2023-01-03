import {
    ModelVariants,
    TrainingProgress,
    TrainingSession,
    TrainingSessionCreated,
} from './dto/models'

export class ApiClient {
    get isMocked() {
        return this.baseUrl === undefined
    }

    constructor(private baseUrl: string | undefined) {
        if (this.isMocked) {
            console.log(`Initialized ApiClient with mocked responses`)
        } else {
            console.log(`Initialized ApiClient for ${baseUrl}`)
        }
    }

    #secureProtocol(protocolName: string): string {
        const s = import.meta.env.DEV ? '' : 's'

        return `${protocolName}${s}://`
    }

    private async baseRequest<T>(
        path: string,
        options: RequestInit,
        mockResponse: T
    ) {
        const { headers, ...otherOptions } = options

        if (this.isMocked) {
            await new Promise(res => setTimeout(res, 3000))
            return mockResponse
        }

        const res = await fetch(
            `${this.#secureProtocol('http')}${this.baseUrl}/${path}`,
            {
                headers: {
                    ...(!(options.body instanceof FormData) && {
                        'Content-Type': 'application/json',
                    }),
                    ...headers,
                },
                ...otherOptions,
            }
        )

        if (!res.ok) {
            throw await FailedRequestError.fromResponse(res)
        } else {
            try {
                const json = await res.json()
                return json as T
            } catch {
                // we assume `T` would be void here
                return null as unknown as T
            }
        }
    }

    getModelVariants = async (): Promise<ModelVariants> => {
        const res = await this.baseRequest<ModelVariants>(
            `models`,
            {
                method: 'GET',
            },
            {
                variants: [
                    {
                        id: '0f5e5af5-9ede-4cc8-814d-f7a0dfb8a6d6',
                        name: 'LSTM',
                        description:
                            'Sequential model generating each timestep one by one.',
                    },
                    {
                        id: 'eafdabd3-fe56-474d-91be-7a9eeeed2124',
                        name: 'GAN',
                        description:
                            'Generative model generating the whole song at once.',
                    },
                ],
            }
        )

        return res
    }

    registerTraining = async (
        modelId: string,
        files: File[]
    ): Promise<TrainingSessionCreated> => {
        const formData = new FormData()
        formData.append('model_id', modelId)
        for (const file of files) {
            formData.append(`files`, file)
        }

        const res = await this.baseRequest<TrainingSessionCreated>(
            `training/register`,
            {
                method: 'POST',
                body: formData,
            },
            { session_id: '123123123' }
        )

        return res
    }

    getTrainingSession = async (
        sessionId: string
    ): Promise<TrainingSession> => {
        const res = await this.baseRequest<TrainingSession>(
            `training/${sessionId}`,
            {
                method: 'GET',
            },
            {
                session_id: '123',
                model: {
                    id: '0f5e5af5-9ede-4cc8-814d-f7a0dfb8a6d6',
                    name: 'LSTM',
                    description:
                        'Sequential model generating each timestep one by one.',
                },
                created_at: '2023-01-03T11:11:13.238Z',
                training_file_names: ['file.mid', 'otherfile.mid'],
            }
        )

        return res
    }

    // returns closing function
    trainingProgress = (
        sessionId: string,
        onMessage: (msg: TrainingProgress) => void
    ): (() => void) => {
        const ws = new WebSocket(
            `${this.#secureProtocol('ws')}${
                this.baseUrl
            }/training/${sessionId}/progress/ws`
        )

        ws.onmessage = event => {
            const msg = JSON.parse(event.data) as TrainingProgress

            onMessage(msg)

            if (msg.finished) {
                ws.close()
            }
        }

        return () => ws.close()
    }
}

export class FailedRequestError extends Error {
    constructor(public response: Response, message: string | undefined) {
        super(message)
    }

    static async fromResponse(response: Response): Promise<FailedRequestError> {
        return new FailedRequestError(response, (await response.json())?.detail)
    }
}
