import axios from 'axios'
import { useAccessStore } from '../stores/access.store'

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json'
    }
})

// Request Interceptor: Attach Token
apiClient.interceptors.request.use(config => {
    const accessStore = useAccessStore()
    if (accessStore.token) {
        config.headers.Authorization = `Bearer ${accessStore.token}`
    }
    return config
})

// Response Interceptor: Handle 401
apiClient.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            const accessStore = useAccessStore()
            accessStore.logout()
        }
        return Promise.reject(error)
    }
)

export default apiClient
