<script setup lang="ts">
import { computed } from 'vue'
import { useForecastStore } from '../../stores/forecast.store'
import { formatMadridDateTime } from '../../utils/dateFormatter'
import Badge from '../atoms/Badge.vue'
import SliderInput from '../atoms/SliderInput.vue'

const forecastStore = useForecastStore()

// Get timestamps from the first available model (assuming all models have same time steps)
const hourly = computed(() => {
    const data = forecastStore.selectedDownloadedData?.data
    if (!data) return null
    return data.hourly || data
})

const timestamps = computed(() => {
    return hourly.value?.time || []
})

const totalSteps = computed(() => timestamps.value.length)

// Format current time
const currentFormattedTime = computed(() => {
    if (!timestamps.value.length) return ''
    const iso = timestamps.value[forecastStore.selectedTimeIndex]
    if (!iso) return ''
    return formatMadridDateTime(iso)
})

</script>

<template>
  <div v-if="totalSteps > 0" class="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-20 w-full max-w-md px-4">
    <div class="bg-slate-900/90 backdrop-blur-md border border-slate-700 rounded-2xl p-4 shadow-2xl">
        
        <div class="flex justify-between items-center mb-2">
            <Badge :text="currentFormattedTime" customClass="bg-slate-800 text-white" />
            <span class="text-xs text-slate-400">
                {{ forecastStore.selectedTimeIndex + 1 }} / {{ totalSteps }}
            </span>
        </div>

        <SliderInput 
            :max="totalSteps - 1" 
            :modelValue="forecastStore.selectedTimeIndex"
            @update:modelValue="(val) => forecastStore.selectedTimeIndex = val"
        />
        
        <div class="flex justify-between mt-2 text-[10px] text-slate-500 uppercase tracking-wider font-semibold">
            <span>Inicio</span>
            <span>Fin</span>
        </div>
    </div>
  </div>
</template>
