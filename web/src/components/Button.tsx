import { FC, ReactNode } from 'react'

interface Props {
    onClick: () => void
    children: ReactNode
}

const Button: FC<Props> = ({ onClick, children }) => {
    return (
        <button
            className="appearance-none rounded-md bg-black px-3 py-2 text-center text-white dark:bg-white dark:text-black"
            onClick={onClick}
        >
            {children}
        </button>
    )
}

export default Button
