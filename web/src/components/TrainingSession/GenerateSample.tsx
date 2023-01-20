import { FC } from 'react'
import { useTrainingSessionContext } from '../../stores/TrainingSessionContext'
import ErrorMessage from '../ErrorMessage'
import LoadingIndicator from '../LoadingIndicator'
import PianoKeyboard from './PianoKeyboard'

const TrainingSession: FC = () => {
    const { generateSample, generateSampleLoading, generateSampleError } =
        useTrainingSessionContext()

    return (
        <div className="text-center">
            <h4 className="mb-10  text-xl">
                Pick a key to generate a new music sample!
            </h4>
            <PianoKeyboard
                onClick={generateSample}
                disabled={generateSampleLoading}
            />
            {generateSampleLoading && (
                <LoadingIndicator message="Generating a midi sample" />
            )}
            {generateSampleError && (
                <ErrorMessage error={generateSampleError}>
                    Failed to generate a sample, try again.
                </ErrorMessage>
            )}
        </div>
    )
}

export default TrainingSession
