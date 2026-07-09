<template>
    <div class="bg-white p-8 rounded-lg shadow-lg">
        <div class="flex justify-center items-center mb-6">
            <BrandIdentity />
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
            <div>
                <label for="email" class="block text-sm font-medium text-gray-700">Email/Username</label>
                <input v-model="username" id="username" type="text" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-black" />
            </div>
            <div>
                <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
                <input v-model="password" id="password" type="password" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-black" />
            </div>
            <button type="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-brass hover:bg-brass-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brass">
                Sign In
            </button>
        </form>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAccessStore } from '../stores/access.store'
import BrandIdentity from '../components/molecules/BrandIdentity.vue';

const username = ref('')
const password = ref('')
const router = useRouter()
const accessStore = useAccessStore()

const handleLogin = async () => {
    if (username.value && password.value) {
        const success = await accessStore.login(username.value, password.value)
        if (success) {
            router.push({ name: 'dashboard' })
        } else {
            alert('Login failed. Please check your credentials.')
        }
    }
}
</script>
