<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAccessStore } from '../../stores/access.store'
import { LogOut, Menu } from 'lucide-vue-next'
import BrandIdentity from '../molecules/BrandIdentity.vue'

const router = useRouter()
const accessStore = useAccessStore()

const emit = defineEmits(['toggle-sidebar'])

const userName = computed(() => accessStore.user?.name || 'User')
const userInitials = computed(() => userName.value.substring(0, 2).toUpperCase())

const handleLogout = () => {
    accessStore.logout()
    router.push({ name: 'login' })
}
</script>

<template>
  <nav class="w-full h-16 flex items-center justify-between px-4 md:px-6 bg-white border-b border-slate-200 shadow-sm relative z-50">
    <div class="flex items-center gap-3">
        <!-- Mobile Menu Button -->
        <button @click="$emit('toggle-sidebar')" class="p-2 -ml-2 text-slate-500 hover:bg-slate-100 rounded-lg md:hidden">
            <Menu class="w-6 h-6" />
        </button>
        
        <!-- Brand -->
        <BrandIdentity />
    </div>

    <!-- User Controls -->
    <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-3 bg-slate-100/50 rounded-full px-3 py-1 border border-slate-200">
            <div class="w-8 h-8 rounded-full bg-brass/20 flex items-center justify-center text-brass font-bold text-sm">
                {{ userInitials }}
            </div>
            <span class="text-sm font-medium text-slate-700 hidden sm:block">{{ userName }}</span>
        </div>
        
        <button @click="handleLogout" class="p-2 text-slate-500 hover:text-red-600 transition-colors rounded-full hover:bg-red-50" title="Logout">
            <LogOut class="w-5 h-5" />
        </button>
    </div>
  </nav>
</template>

<style scoped>
</style>
