<script setup lang="ts">
import { computed, ref } from 'vue'
import { Download, Loader2 } from 'lucide-vue-next'
import type { DownloadedData } from '../../types'
import { formatMadridDateTime } from '../../utils/dateFormatter'
import ModalHeader from '../molecules/ModalHeader.vue'
import ForecastDesktopTable from './ForecastDesktopTable.vue'
import ForecastMobileList from './ForecastMobileList.vue'
import { generateForecastPdf } from '../../utils/forecastPdfGenerator'
import { getWindTailwindClass, getCotaTailwindClass } from '../../utils/wave-colors'

const dockElevation = computed(() => props.zoneInfo?.dock_elevation)

const getCotaBgColor = (cotaValue: number | undefined): string => {
    const de = dockElevation.value
    if (cotaValue === undefined || !de || de <= 0) return ''
    return getCotaTailwindClass(cotaValue / de)
}

const getWindBgColor = (speed: number | undefined): string => {
    return getWindTailwindClass(speed)
}

const props = defineProps<{
  isOpen: boolean
  data: DownloadedData | null
  hindcastInfo: any
  zoneInfo?: any
}>()

const emit = defineEmits(['close'])

const isGeneratingPdf = ref(false)

async function downloadPdf() {
    if (!props.data || !hourlyData.value.length) return
    isGeneratingPdf.value = true
    try {
        await generateForecastPdf(
            hourlyData.value,
            models.value,
            props.zoneInfo ?? null,
            props.hindcastInfo ?? null,
            props.data.downloaded_at,
        )
    } finally {
        isGeneratingPdf.value = false
    }
}

// Helper to format date (hora local de Madrid)
const formatDate = (isoString: string) => formatMadridDateTime(isoString)

// Extract hourly data object (handle both nested 'hourly' and flat structure)
const hourly = computed(() => {
    if (!props.data?.data) return null
    return props.data.data.hourly || props.data.data
})

// Extract models dynamically from keys (e.g. wave_height_ewam -> ewam)
const models = computed(() => {
    if (!hourly.value) return []
    const keys = Object.keys(hourly.value)
    const modelSet = new Set<string>()
    keys.forEach(key => {
        if (key.startsWith('wave_height_')) {
            modelSet.add(key.replace('wave_height_', ''))
        }
    })
    return Array.from(modelSet)
})

const hourlyData = computed(() => {
    const h = hourly.value
    if (!h || !h.time) return []

    // La marea no depende del modelo, así que se toma del primero que la tenga disponible.
    const tideKey = models.value
        .map(m => `tide_level_${m}`)
        .find(key => h[key] !== undefined)

    return h.time.map((t: string, i: number) => {
        const row: any = { time: t, tide: tideKey ? h[tideKey]?.[i] : undefined }
        models.value.forEach(m => {
            row[m] = {
                height: h[`wave_height_${m}`]?.[i],
                period: h[`wave_period_${m}`]?.[i],
                direction: h[`wave_direction_${m}`]?.[i],
                cotaRu2p: h[`cota_ru2p_${m}`]?.[i],
                caudalRebase: h[`caudal_rebase_${m}`]?.[i]
            }
        })
        // Wind data (modelo-independiente)
        if (h.wind_speed_10m !== undefined) {
            row.windSpeed = h.wind_speed_10m[i]
            row.windGusts = h.wind_gusts_10m?.[i]
            row.windDirection = h.wind_direction_10m?.[i]
        }
        return row
    })
})

</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-slate-900/80 backdrop-blur-sm" @click="$emit('close')"></div>

    <!-- Modal Content -->
    <div class="relative w-full max-w-7xl h-[90vh] bg-slate-900 border border-slate-700 rounded-xl shadow-2xl flex flex-col overflow-hidden">
        
        <!-- Header Molecule -->
        <ModalHeader :title="'Previsión de Oleaje'" @close="$emit('close')">
            <template #actions>
                <button
                    v-if="data && hourlyData.length"
                    @click="downloadPdf"
                    :disabled="isGeneratingPdf"
                    class="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
                           bg-sky-600 hover:bg-sky-500 disabled:bg-slate-600 disabled:cursor-wait text-white"
                >
                    <Loader2 v-if="isGeneratingPdf" class="w-4 h-4 animate-spin" />
                    <Download v-else class="w-4 h-4" />
                    <span class="hidden sm:inline">{{ isGeneratingPdf ? 'Generando…' : 'Descargar PDF' }}</span>
                </button>
            </template>
            <template #subtitle>
                <p class="text-sm text-slate-400 mt-1" v-if="zoneInfo">
                    Zona: {{ zoneInfo.name }} (ID: {{ zoneInfo.id }}) - Lat: {{ zoneInfo.geom?.coordinates[1]?.toFixed(4) }}, Lon: {{ zoneInfo.geom?.coordinates[0]?.toFixed(4) }}
                </p>
                <p class="text-sm text-slate-400 mt-1" v-else-if="hindcastInfo">
                    Punto de Partida (ID: {{ hindcastInfo.id }}) - Lat: {{ hindcastInfo.latitude.toFixed(4) }}, Lon: {{ hindcastInfo.longitude.toFixed(4) }}
                </p>
                <p class="text-xs text-slate-500 mt-0.5" v-if="data">
                    Descargado: {{ formatDate(data.downloaded_at) }}
                </p>
            </template>
        </ModalHeader>

        <!-- Data Container -->
        <div class="flex-1 overflow-auto custom-scrollbar bg-slate-900">
            <!-- Desktop Table View -->
            <ForecastDesktopTable 
                v-if="data && hourlyData.length"
                :hourlyData="hourlyData"
                :models="models"
                :getCotaColorHelper="getCotaBgColor"
                :getWindColorHelper="getWindBgColor"
                :formatDateHelper="formatDate"
            />
            
            <!-- Mobile Card View -->
            <ForecastMobileList 
                v-if="data && hourlyData.length"
                :hourlyData="hourlyData"
                :models="models"
                :getCotaColorHelper="getCotaBgColor"
                :getWindColorHelper="getWindBgColor"
                :formatDateHelper="formatDate"
            />

            <!-- Empty State -->
            <div v-if="!data || hourlyData.length === 0" class="flex items-center justify-center p-8 text-slate-500 flex-col">
                <p class="text-lg text-center">No hay datos de previsión disponibles.</p>
                <p class="text-sm mt-2 text-center">Intenta seleccionar otro sistema o contacta con soporte.</p>
            </div>
        </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom Scrollbar for dark theme */
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #0f172a; 
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #334155; 
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #475569; 
}
</style>
