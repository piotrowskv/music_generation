import { FC } from 'react'
import FileInput from '../FileInput'

export const midiMimeType = 'audio/midi'

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
                <div className="italic text-gray-400">
                    Upload using the button or drag&drop files onto the tile
                </div>
            </div>
            <FileInput onChange={onChange} accept={midiMimeType}>
                {files.length === 0
                    ? 'Choose files'
                    : `${files.length} file${
                          files.length === 1 ? '' : 's'
                      } uploaded`}
            </FileInput>
        </div>
    )
}

export default UploadFiles
