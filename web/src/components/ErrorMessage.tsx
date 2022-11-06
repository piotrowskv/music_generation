import React, { ReactNode } from 'react'
import Refresh from '../assets/Refresh'

interface Props {
    children: ReactNode
    error?: {}
    onRetry: () => void
}

const ErrorMessage: React.FC<Props> = ({
    children: message,
    error,
    onRetry,
}) => (
    <div className="flex-row text-center">
        <span className="text-red-400">{message}</span>
        {error && <div className="text-red-400">{error.toString()}</div>}
        <button onClick={onRetry} className="group mt-2">
            Retry{' '}
            <Refresh className="inline h-5 w-5 fill-black group-hover:animate-spin-once dark:fill-white" />
        </button>
    </div>
)

export default ErrorMessage
