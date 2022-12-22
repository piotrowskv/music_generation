import { apiClient, testUrlDescribe } from './setup'

testUrlDescribe('fetches models', () => {
    test('happy path', async () => {
        const models = await apiClient.getModelVariants()

        // we got any response
        expect(models).toBeTruthy()

        // we got all models
        expect(models.variants.length).toBe(3)

        // all fields are present
        for (const v of models.variants) {
            expect(v.description).toBeTruthy()
            expect(v.id).toBeTruthy()
            expect(v.name).toBeTruthy()
        }
    })

    test('returned models are unique', async () => {
        const models = await apiClient.getModelVariants()

        const ids = models.variants.map(e => e.id)

        expect(ids.length).toBe(new Set(ids).size)
    })
})
