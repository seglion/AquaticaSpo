import { defineStore } from 'pinia'
import { computed } from 'vue'
import { useStorage } from '@vueuse/core'
// import { useRouter } from 'vue-router'

export const useAccessStore = defineStore('access', () => {
    // Persist token in localStorage
    const token = useStorage('accessToken', '')
    const user = useStorage<any>('user', null) // Store basic user info if needed

    // const router = useRouter()

    const isAuthenticated = computed(() => !!token.value)

    function setToken(newToken: string) {
        token.value = newToken
    }

    function setUser(userData: any) {
        user.value = userData
    }

    async function login(username: string, password: string): Promise<boolean> {
        try {
            // OAuth2 requires form data
            const formData = new FormData()
            formData.append('username', username)
            formData.append('password', password)

            // Import dynamically to avoid circular dependency if client imports store
            // Check src/api/client.ts: it imports store. 
            // Better to pass token in interceptor without importing store at top level if possible, 
            // but for now, let's use the client.
            const { default: api } = await import('../api/client')

            const response = await api.post('/users/login', formData, {
                headers: { 'Content-Type': 'multipart/form-data' } // or application/x-www-form-urlencoded
            })

            const { access_token, user_id } = response.data
            setToken(access_token)

            // Optionally fetch user details?
            // setUser({ id: user_id, name: username }) 
            // For now just store what we have
            setUser({ id: user_id, name: username })

            return true
        } catch (error) {
            console.error('Login failed:', error)
            return false
        }
    }

    function logout() {
        token.value = null
        user.value = null
        // Force reload or redirect
        window.location.href = '/login'
    }

    return {
        token,
        user,
        isAuthenticated,
        setToken,
        setUser,
        login,
        logout
    }
})
