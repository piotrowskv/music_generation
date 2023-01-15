import { FC, ReactNode, useRef } from 'react'
import Button from './Button'

interface Props {
    onChange: (files: File[]) => void
    accept: Set<string>
    children: ReactNode
}

// Wraps HTML5 input[type=file] with a custom button to allow for styling
const FileInput: FC<Props> = ({ onChange, accept, children }) => {
    const fileInputRef = useRef<HTMLInputElement | null>(null)

    return (
        <div>
            <Button onClick={() => fileInputRef.current?.click()}>
                {children}
            </Button>
            <input
                ref={fileInputRef}
                type="file"
                accept={[...accept].join(', ')}
                onChange={e => onChange([...e.target.files!])}
                className="hidden"
                multiple
            />
        </div>
    )
}

export default FileInput
