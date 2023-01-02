import { FC, ReactNode, useRef } from 'react'

interface Props {
    onChange: (files: File[]) => void
    accept: string
    children: ReactNode
}

// Wraps HTML5 input[type=file] with a custom button to allow for styling
const FileInput: FC<Props> = ({ onChange, accept, children }) => {
    const fileInputRef = useRef<HTMLInputElement | null>(null)

    return (
        <div>
            <button
                className="cursor-pointer appearance-none rounded-md bg-black px-3 py-2 text-center text-white dark:bg-white dark:text-black"
                onClick={() => fileInputRef.current?.click()}
            >
                {children}
            </button>
            <input
                ref={fileInputRef}
                type="file"
                accept={accept}
                onChange={e => onChange([...e.target.files!])}
                className="hidden"
                multiple
            />
        </div>
    )
}

export default FileInput
