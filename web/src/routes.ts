import { createRouting, segment, string } from 'ts-routes'

export const routes = createRouting({
    root: segment`/`,
    trainingSession: segment`/session/${string('sessionId')}`,
})
