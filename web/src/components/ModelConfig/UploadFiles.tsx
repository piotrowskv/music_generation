import { FC } from 'react'
import FileInput from '../FileInput'

export const midiMimeTypes = new Set(['audio/midi', 'audio/mid'])

interface Props {
    files: File[]
    onChange: (files: File[]) => void
}

const UploadFiles: FC<Props> = ({ files, onChange }) => {
    return (
        <div className="flex items-center justify-between">
            <div>
                <label htmlFor="model-midi-files" className="text-xl">
                    Upload MIDI files
                </label>
                <div className="italic text-gray">
                    Upload using the button or drag&drop files onto the tile
                </div>
            </div>
            <FileInput onChange={onChange} accept={midiMimeTypes}>
                {files.length === 0
                    ? 'Choose files'
                    : `${files.length} file${
                          files.length === 1 ? '' : 's'
                      } chosen`}
            </FileInput>
        </div>
    )
}

export default UploadFiles
