import { useCallback, useEffect, useRef, useState } from 'react'

export type UseAsyncResult<T extends unknown[], U extends {}> = {
    call: (...args: T) => Promise<U | undefined>
    result: U | undefined
    loading: boolean
    error: {} | undefined
}

export function useAsync<T extends unknown[], U extends {}>(
    func: (...args: T) => Promise<U>
): UseAsyncResult<T, U> {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<{} | undefined>(undefined)
    const [result, setResult] = useState<U | undefined>(undefined)
    const cancelled = useRef(false)

    useEffect(() => {
        cancelled.current = false
        return () => {
            cancelled.current = true
        }
    }, [])

    const call = useCallback(
        async (...args: T) => {
            setError(undefined)
            setResult(undefined)
            setLoading(true)

            try {
                const res = await func(...args)
                if (!cancelled.current) {
                    setResult(res)
                    setLoading(false)
                }
                return res
            } catch (err) {
                if (!cancelled.current) {
                    setError(err as {})
                    setLoading(false)
                }
            }
        },
        [func, cancelled]
    )

    return { call, result, loading, error }
}
