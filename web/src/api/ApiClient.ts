import { ModelVariants } from './dto/models'

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

        const res = await fetch(`${this.baseUrl}/${path}`, {
            headers: {
                'Content-Type': 'application/json',
                ...headers,
            },
            ...otherOptions,
        })

        if (!res.ok) {
            throw new FailedRequestError(res)
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
}

export class FailedRequestError extends Error {
    constructor(public response: Response) {
        super()
    }
}