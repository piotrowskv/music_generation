export class ApiClient {
    constructor(private baseUrl: string) {
        console.log(`Initialized ApiClient for ${baseUrl}`)
    }

    private async baseRequest<T>(path: string, options: RequestInit = {}) {
        const { headers, ...otherOptions } = options

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
}

export class FailedRequestError extends Error {
    constructor(public response: Response) {
        super()
    }
}
