import clsx from 'clsx'
import { FC } from 'react'
import { ModelTraining } from '../../stores/ModelConfigContext'
import './PickTraining.css'

interface Props {
    modelTraining: ModelTraining | undefined
    onChange: (mode: ModelTraining) => void
}

const PickTraining: FC<Props> = ({ modelTraining, onChange }) => {
    const handleChange = (mode: ModelTraining) => {
        if (modelTraining !== mode) {
            onChange(mode)
        }
    }

    return (
        <div className="flex">
            <div className="w-3/5">
                <label htmlFor="model-training" className="text-xl">
                    Pick training
                </label>
                {modelTraining !== undefined && (
                    <div className="italic text-gray-400">
                        {(() => {
                            switch (modelTraining) {
                                case ModelTraining.pretrained:
                                    return 'Use a model that was previously trained'
                                case ModelTraining.trainMyself:
                                    return 'Train a vanilla model by providing MIDI files to train on'
                            }
                        })()}
                    </div>
                )}
            </div>

            <div className="relative min-h-[40px] w-2/5">
                <Toggle
                    className="absolute right-0 bg-black text-white dark:bg-white dark:text-black"
                    onClick={handleChange}
                />
                <Toggle
                    className={clsx(
                        'toggle-overlay absolute right-0 bg-white text-black dark:bg-black dark:text-white',
                        modelTraining === ModelTraining.pretrained &&
                            'toggle-overlay-left',
                        modelTraining === ModelTraining.trainMyself &&
                            'toggle-overlay-right'
                    )}
                    onClick={handleChange}
                />
            </div>
        </div>
    )
}

const Toggle: FC<{
    className: string
    onClick: (value: ModelTraining) => void
}> = ({ className, onClick }) => (
    <div className={clsx('flex gap-4 rounded-md p-2', className)}>
        <button onClick={() => onClick(ModelTraining.pretrained)}>
            pre-trained
        </button>
        <button onClick={() => onClick(ModelTraining.trainMyself)}>
            train myself
        </button>
    </div>
)

export default PickTraining
