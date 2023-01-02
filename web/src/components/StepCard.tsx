import clsx from 'clsx'
import { FC, ReactNode, useRef, useState } from 'react'

interface Props {
    completed: boolean
    children: ReactNode
    onDrop?: (files: File[]) => void
}

const StepCard: FC<Props> = ({ completed, children, onDrop }) => {
    const dragRc = useRef(0)
    const [isDropHovering, setIsDropHovering] = useState(false)

    const updateDragRc = (delta: number) => {
        dragRc.current += delta
        setIsDropHovering(dragRc.current !== 0)
    }

    const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()
        updateDragRc(1)
    }
    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()
        updateDragRc(-1)
    }
    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()
    }
    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()
        onDrop!([...e.dataTransfer.files!])
        dragRc.current = 0
        setIsDropHovering(false)
    }

    return (
        <div
            className={clsx(
                'w-full rounded-xl border-4 border-black p-4 dark:border-white',
                completed ? 'border-solid' : 'border-dashed',
                isDropHovering && 'animate-[wiggle_0.7s_ease-in-out_infinite]'
            )}
            {...(onDrop && {
                onDrop: handleDrop,
                onDragOver: handleDragOver,
                onDragEnter: handleDragEnter,
                onDragLeave: handleDragLeave,
            })}
        >
            {children}
        </div>
    )
}

export default StepCard
