import clsx from 'clsx'
import { FC, ReactNode } from 'react'

interface Props {
    completed: boolean
    children: ReactNode
}

const StepCard: FC<Props> = ({ completed, children }) => (
    <div
        className={clsx(
            'w-full rounded-xl border-4 border-black p-4 dark:border-white',
            completed ? 'border-solid' : 'border-dashed'
        )}
    >
        {children}
    </div>
)

export default StepCard
