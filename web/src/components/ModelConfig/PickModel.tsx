import { FC } from 'react'
import { ModelVariant } from '../../api/models/models'

interface Props {
    models: ModelVariant[]
}

const PickModel: FC<Props> = ({ models }) => {
    return (
        <div className="flex items-center justify-between">
            <label htmlFor="model-select" className="text-xl">
                Pick model
            </label>

            <select
                name="model"
                id="model-select"
                className="cursor-pointer appearance-none rounded-md bg-black px-3 py-2 text-center text-white dark:bg-white dark:text-black"
            >
                <option value="">...</option>
                {models.map(e => (
                    <option value={e.id}>{e.name}</option>
                ))}
            </select>
        </div>
    )
}

export default PickModel
