import { ChangeEvent, FC } from 'react'
import { ModelVariant } from '../../api/models/models'

interface Props {
    models: ModelVariant[]
    selectedModel: ModelVariant | undefined
    onChangePickedModel: (id: string | undefined) => void
}

const PickModel: FC<Props> = ({
    models,
    onChangePickedModel,
    selectedModel,
}) => {
    const onChange = ({ target }: ChangeEvent<HTMLSelectElement>) => {
        const value = target.value

        onChangePickedModel(value || undefined)
    }

    return (
        <div className="flex items-center justify-between">
            <div>
                <label htmlFor="model-select" className="text-xl">
                    Pick model
                </label>
                {selectedModel && (
                    <div className="italic text-gray-400">
                        {selectedModel.description}
                    </div>
                )}
            </div>

            <select
                name="model"
                id="model-select"
                className="cursor-pointer appearance-none rounded-md bg-black px-3 py-2 text-center text-white dark:bg-white dark:text-black"
                onChange={onChange}
                defaultValue={selectedModel?.id}
            >
                <option value="">...</option>
                {models.map(e => (
                    <option value={e.id} key={e.id}>
                        {e.name}
                    </option>
                ))}
            </select>
        </div>
    )
}

export default PickModel
