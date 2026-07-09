<template>
    <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm">
        <div class="flex items-center">
            <h1 class="text-xl font-bold text-parchment">{{ title }}</h1>
        </div>

        <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-3">
                <div class="w-8 h-8 rounded-full bg-brass/20 flex items-center justify-center text-brass font-bold text-sm">
                    {{ userInitials }}
                </div>
                <span class="text-sm font-medium text-slate-700 hidden sm:block">{{ userName }}</span>
            </div>
            
            <div class="h-6 w-px bg-slate-200 mx-2"></div>

            <button @click="handleLogout" class="p-2 text-slate-500 hover:text-red-600 transition-colors" title="Logout">
                <LogOut class="w-5 h-5" />
            </button>
        </div>
    </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAccessStore } from '../../stores/access.store'
import { LogOut } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const accessStore = useAccessStore()

const title = computed(() => {
    return route.name === 'dashboard' ? 'Forecast Systems' : 
           route.name === 'map' ? 'Global Map View' : 'Dashboard'
})

const userName = computed(() => accessStore.user?.name || 'User')
const userInitials = computed(() => userName.value.substring(0, 2).toUpperCase())

const handleLogout = () => {
    accessStore.logout()
    router.push({ name: 'login' })
}
</script>
