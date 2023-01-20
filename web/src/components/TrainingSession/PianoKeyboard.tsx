import clsx from 'clsx'
import React, { CSSProperties } from 'react'

interface Props {
    onClick: (key: number) => void
    disabled: boolean
}

const PianoKeyboard: React.FC<Props> = ({ onClick, disabled }) => (
    <div
        className={clsx(
            'relative',
            disabled && 'pointer-events-none select-none blur-sm'
        )}
    >
        {[1, 3, 5, 7, 9, 11, 13].map(key => (
            <WhiteKey onClick={() => onClick(key)} className="inline-block" />
        ))}
        {[2, 4, 8, 10, 12].map(key => (
            <BlackKey
                style={{ '--mult': key }}
                onClick={() => onClick(key)}
                className="absolute left-[calc(theme(spacing.24)*(var(--mult)/2)-theme(spacing.12)/2)] top-0"
            />
        ))}
    </div>
)

interface WhiteKeyProps {
    onClick: () => void
    className?: string | undefined
}

const WhiteKey: React.FC<WhiteKeyProps> = ({ onClick, className }) => {
    return (
        <div
            className={clsx(
                'h-60 w-24 cursor-pointer rounded-xl border-2 border-black bg-white hover:bg-gray',
                className
            )}
            onClick={onClick}
        ></div>
    )
}

interface BlackKeyProps {
    onClick: () => void
    className?: string | undefined
    style?: CSSProperties | undefined
}

const BlackKey: React.FC<BlackKeyProps> = ({ onClick, className, style }) => {
    return (
        <div
            style={style}
            className={clsx(
                'h-40 w-12 cursor-pointer rounded-xl border-2 border-white bg-black hover:bg-gray',
                className
            )}
            onClick={onClick}
        ></div>
    )
}

export default PianoKeyboard
