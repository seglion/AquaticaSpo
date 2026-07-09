<template>
    <div class="flex flex-col h-full text-parchment">

        <nav class="flex-1 px-4 py-6 space-y-2 overflow-y-auto custom-scrollbar">
            <div v-if="forecastStore.loading" class="text-center text-slate-400 text-sm py-4">
                Loading systems...
            </div>

            <div v-else-if="forecastStore.error" class="text-center text-red-400 text-xs py-4 px-2 bg-red-900/10 rounded border border-red-500/20">
                {{ forecastStore.error }}
            </div>
            
            <template v-else>
                <div v-for="system in forecastStore.systems" :key="system.id">
                    <router-link :to="{name: 'dashboard', query: { systemId: system.id }}" custom v-slot="{ navigate, href }">
                        <a :href="href" @click="navigate" class="block outline-none">
                            <SidebarItem 
                                :icon="Activity" 
                                :label="system.name" 
                                :isActive="String($route.query.systemId) === String(system.id)"
                            />
                        </a>
                    </router-link>
                </div>
            </template>
        </nav>

    </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useForecastStore } from '../../stores/forecast.store'
import { Activity } from 'lucide-vue-next'
import SidebarItem from '../molecules/SidebarItem.vue'

const router = useRouter()
const route = useRoute()
const forecastStore = useForecastStore()

onMounted(async () => {
    await forecastStore.fetchSystems()

    const currentId = route.query.systemId
    if (currentId) {
        // URL already has a systemId but systems weren't loaded yet when the
        // DashboardLayout watcher fired — call selectSystem now that they are.
        await forecastStore.selectSystem(Number(currentId))
    } else if (forecastStore.systems.length > 0) {
        const firstSystem = forecastStore.systems[0]
        if (firstSystem) {
            router.replace({ name: 'dashboard', query: { systemId: firstSystem.id } })
        }
    }
})
</script>
