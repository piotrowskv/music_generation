import { FC } from 'react'

type Props = {
    message: string
}

const LoadingIndicator: FC<Props> = ({ message }) => (
    <span className="animate-pulse">{message}</span>
)

export default LoadingIndicator
