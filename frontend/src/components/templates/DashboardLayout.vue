<template>
  <div class="h-screen w-screen flex flex-col overflow-hidden bg-slate-50">
    <!-- Top Navbar (Static) -->
    <Navbar class="flex-shrink-0 z-30" @toggle-sidebar="isSidebarOpen = !isSidebarOpen" />

    <!-- Main Layout Wrapper -->
    <div class="flex-1 flex overflow-hidden relative">
        
        <!-- Mobile Backdrop -->
        <div v-if="isSidebarOpen" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 md:hidden" @click="isSidebarOpen = false"></div>

        <!-- Sidebar -->
        <!-- Mobile: Fixed, Slide-in. Desktop: Static, Always visible. -->
        <aside 
            class="fixed inset-y-0 left-0 z-50 w-72 bg-slate-900 border-r border-slate-800 transition-transform duration-300 transform md:relative md:translate-x-0 flex-shrink-0"
            :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
        >
            <Sidebar />
        </aside>

        <!-- Content Wrapper -->
        <main class="flex-1 relative flex flex-col min-w-0">
            <!-- Map (Background of Content) -->
            <!-- Map (Background of Content) -->
            <MapContainer 
                class="absolute inset-0 z-0" 
                @open-forecast="(evt) => { console.log('Dashboard received open-forecast', evt); isForecastModalOpen = true }"
                @open-webcam="(cam) => { console.log('Dashboard received open-webcam', cam); selectedWebcam = cam; isWebcamModalOpen = true }" 
            />
            
            <!-- Time Slider (Floating Overlay) -->
            <TimeSlider />
            
            <!-- Forecast Modal -->
            <ForecastModal 
                :isOpen="isForecastModalOpen" 
                :data="forecastStore.selectedZoneId ? forecastStore.selectedZoneData : forecastStore.selectedDownloadedData"
                :hindcastInfo="forecastStore.selectedHindcastPoint"
                :zoneInfo="forecastStore.selectedZoneId ? forecastStore.forecastZones.find(z => z.id === forecastStore.selectedZoneId) : null"
                @close="isForecastModalOpen = false"
            />

            <!-- Webcam Modal -->
            <WebcamModal
                :isOpen="isWebcamModalOpen"
                :webcam="selectedWebcam"
                @close="isWebcamModalOpen = false"
            />

            <!-- Page Content (Overlay) -->
            <!-- Used for specific views or overlays. If the view needs interaction, it should manage its own pointer-events or background. -->
            <div class="relative z-10 flex-1 overflow-y-auto pointer-events-none">
                 <div class="pointer-events-none min-h-full">
                    <router-view></router-view>
                 </div>
            </div>
        </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useForecastStore } from '../../stores/forecast.store'
import Sidebar from '../organisms/Sidebar.vue'
import Navbar from '../organisms/Navbar.vue'
import MapContainer from '../organisms/MapContainer.vue'
import TimeSlider from '../organisms/TimeSlider.vue'
import ForecastModal from '../organisms/ForecastModal.vue'
import WebcamModal from '../organisms/WebcamModal.vue'
import type { MeteoGaliciaWebcam } from '../../api/webcams.service'

const isSidebarOpen = ref(false)
const isForecastModalOpen = ref(false)
const isWebcamModalOpen = ref(false)
const selectedWebcam = ref<MeteoGaliciaWebcam | null>(null)
const route = useRoute()
const forecastStore = useForecastStore()

onMounted(() => {
    console.log('DashboardLayout mounted')
})

// React to system selection
watch(() => route.query.systemId, async (newId) => {
    console.log('DashboardLayout: systemId changed to', newId)
    if (newId) {
        await forecastStore.selectSystem(Number(newId))
    }
}, { immediate: true })
</script>
