// kept as an enum to prevent repetitions
export enum DataTestId {
    'dummy',
}

export const dataTestAttr = (key: keyof typeof DataTestId) => ({
    'data-testid': key,
})
