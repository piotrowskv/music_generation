import { apiUrl } from '../utils/config'
import { ApiClient } from './ApiClient'

export const apiClient = new ApiClient(apiUrl)
