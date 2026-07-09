<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const map = ref<L.Map | null>(null)

onMounted(() => {
  // Center of Galicia (North West Spain): [43.0, -8.0]
  map.value = L.map('map', {
    zoomControl: false,
    attributionControl: false
  }).setView([43.0, -8.0], 7)

  if (map.value) {
    // Create custom pane for forecast and hindcast points to ensure they render above webcam markers
    map.value.createPane('forecastPane')
    map.value.getPane('forecastPane')!.style.zIndex = '650'

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    }).addTo(map.value as L.Map)
  }
})

// Watch for port changes to center map
import { watch } from 'vue'
import { useForecastStore } from '../../stores/forecast.store'

const forecastStore = useForecastStore()

watch(() => forecastStore.selectedPort, (newPort) => {
    if (newPort && map.value) {
        console.log('Centering map on port:', newPort)
        // Use flyTo for smooth animation
        map.value.flyTo([newPort.latitude, newPort.longitude], 15, {
            duration: 2.0
        })
    }
})

const emit = defineEmits(['open-forecast', 'open-webcam'])

// Draw Hindcast Point
const hindcastLayer = ref<L.CircleMarker | null>(null)
import { getWaveColor } from '../../utils/wave-colors'

// Helper to get average wave height for current time
const getCurrentAverageWaveHeight = () => {
    const data = forecastStore.selectedDownloadedData?.data
    if (!data) return undefined
    
    // Support both nested and flat structure
    const hourly = data.hourly || data
    if (!hourly) return undefined

    const keys = Object.keys(hourly)
    const heightKeys = keys.filter(k => k.startsWith('wave_height_'))
    
    if (heightKeys.length === 0) return undefined

    let sum = 0
    let count = 0
    const index = forecastStore.selectedTimeIndex

    heightKeys.forEach(key => {
        const val = hourly[key]?.[index]
        if (val !== undefined && val !== null) {
            sum += val
            count++
        }
    })

    return count > 0 ? sum / count : undefined
}

import { fetchNearbyWebcams } from '../../api/webcams.service'
const webcamsLayer = ref<L.LayerGroup | null>(null)

const loadWebcamsForPoint = async (lat: number, lon: number) => {
    try {
        const results = await fetchNearbyWebcams(lat, lon, 100);
        
        if (webcamsLayer.value && map.value) {
            map.value.removeLayer(webcamsLayer.value as any);
        }

        const markers = results.map(cam => {
            const icon = L.divIcon({
                html: `
                    <div class="w-7 h-7 rounded-full border-2 border-slate-800 overflow-hidden shadow-[0_0_10px_rgba(0,0,0,0.5)] bg-slate-900 transition-transform hover:scale-150 hover:border-sky-500 hover:z-50 relative group cursor-pointer block">
                        <img src="${cam.imaxeCamaraMini}?t=${new Date().getTime()}" class="w-full h-full object-cover"/>
                        <div class="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors"></div>
                    </div>
                `,
                className: 'custom-webcam-icon bg-transparent border-none',
                iconSize: [28, 28],
                iconAnchor: [14, 14]
            });

            return L.marker([cam.lat, cam.lon], { icon })
                .bindTooltip(cam.nomeCamara, {
                    direction: 'top',
                    offset: [0, -10],
                    className: 'bg-slate-800 text-slate-100 border-slate-700 shadow-xl rounded-lg px-2 py-1 text-xs font-semibold'
                })
                .on('click', () => {
                    emit('open-webcam', cam);
                });
        });

        if (map.value) {
           webcamsLayer.value = L.layerGroup(markers).addTo(map.value as L.Map);
        }
    } catch(err) {
        console.error('Error rendering webcams:', err);
    }
}

// Watch for point selection to draw marker
watch(() => forecastStore.selectedHindcastPoint, (point) => {
    // Remove existing layer
    if (hindcastLayer.value && map.value) {
        map.value.removeLayer(hindcastLayer.value as any)
        hindcastLayer.value = null
    }

    // Fix styling of pulse-fast animation to not bleed outside circle
    if (point && map.value) {
        // Initial draw
        const avgHeight = getCurrentAverageWaveHeight()
        const color = getWaveColor(avgHeight)
        const isHighWave = avgHeight !== undefined && avgHeight >= 2

        console.log('Drawing hindcast point:', point, 'Avg Height:', avgHeight, 'Color:', color)
        
        hindcastLayer.value = L.circleMarker([point.latitude, point.longitude], {
            pane: 'forecastPane',
            radius: 10,
            fillColor: color,
            fillOpacity: 0.9,
            stroke: true, 
            color: '#1e293b', // Add dark border to make it distinct
            weight: 2,
            className: isHighWave ? 'animate-pulse-fast' : '' // Blink if orange/red
        }).addTo(map.value as L.Map)
        .on('click', () => {
             console.log('Hindcast marker clicked - emitting open-forecast')
             forecastStore.selectedZoneId = null
             forecastStore.selectedZoneData = null // Clear zone selection to show main point data
             emit('open-forecast', { type: 'hindcast' })
        })

        // Webcams Rendering Logic
        loadWebcamsForPoint(point.latitude, point.longitude)
    } else {
        if (webcamsLayer.value && map.value) {
            map.value.removeLayer(webcamsLayer.value as any)
            webcamsLayer.value = null
        }
    }
})



// Helper to get average wave height for a specific zone
const getZoneAverageWaveHeight = (zoneId: number) => {
    const zoneData = forecastStore.forecastZonesData[zoneId]
    if (!zoneData) return undefined
    
    // Support both nested and flat structure
    const data = zoneData.data
    if (!data) return undefined

    const hourly = data.hourly || data
    if (!hourly) return undefined

    const keys = Object.keys(hourly)
    const heightKeys = keys.filter(k => k.startsWith('wave_height_'))
    
    if (heightKeys.length === 0) return undefined

    let sum = 0
    let count = 0
    const index = forecastStore.selectedTimeIndex

    heightKeys.forEach(key => {
        const val = hourly[key]?.[index]
        if (val !== undefined && val !== null) {
            sum += val
            count++
        }
    })

    return count > 0 ? sum / count : undefined
}


// Draw Forecast Zones (Propagated Points)
const forecastZonesLayer = ref<L.LayerGroup | null>(null)

watch(
    [() => forecastStore.forecastZones, () => forecastStore.forecastZonesData, () => forecastStore.selectedTimeIndex], 
    ([zones, _zonesData, _timeIndex]) => {
    // Remove existing layer group
    if (forecastZonesLayer.value && map.value) {
        map.value.removeLayer(forecastZonesLayer.value as any)
        forecastZonesLayer.value = null
    }

    if (zones && zones.length > 0 && map.value) {
        // console.log('Drawing forecast zones:', zones)
        const markers = zones.map(zone => {
            const avgHeight = getZoneAverageWaveHeight(zone.id)
            const color = getWaveColor(avgHeight)
            const isHighWave = avgHeight !== undefined && avgHeight >= 2

            return L.circleMarker([zone.geom.coordinates[1], zone.geom.coordinates[0]], {
                pane: 'forecastPane',
                radius: 6,
                fillColor: color, // Dynamic color
                color: '#FFFFFF',
                weight: 1,
                opacity: 0.8,
                fillOpacity: 0.8,
                className: isHighWave ? 'animate-pulse-fast' : ''
            })
            .bindTooltip(zone.name, {
                permanent: false,
                direction: 'top',
                className: 'bg-slate-800 text-white border-none rounded px-2 py-1 text-xs'
            })
            .on('click', () => {
                console.log('Zone clicked:', zone.id)
                // Set the selected data in store for the modal to use
                forecastStore.selectedZoneId = zone.id
                forecastStore.selectedZoneData = forecastStore.forecastZonesData[zone.id] || null
                // Signal that we are viewing a zone, not the main point (optional, or use selectedZoneData presence)
                emit('open-forecast', { type: 'zone', id: zone.id, name: zone.name })
            })
        })
        
        forecastZonesLayer.value = L.layerGroup(markers).addTo(map.value as L.Map)
    }
}, { deep: true })

// Watch for time index or data changes to update color
watch(
    [() => forecastStore.selectedTimeIndex, () => forecastStore.selectedDownloadedData],
    () => {
        // Update Hindcast Point
        if (hindcastLayer.value) {
            const avgHeight = getCurrentAverageWaveHeight()
            const color = getWaveColor(avgHeight)
            const isHighWave = avgHeight !== undefined && avgHeight >= 2
            
            hindcastLayer.value.setStyle({
                fillColor: color,
                className: isHighWave ? 'animate-pulse-fast' : ''
            })
            
            // Ensure class update
            if (hindcastLayer.value.getElement()) {
                 const el = hindcastLayer.value.getElement()
                 if (el) {
                     if (isHighWave) {
                         el.classList.add('animate-pulse-fast')
                     } else {
                         el.classList.remove('animate-pulse-fast')
                     }
                 }
            }
        }

    }
)

// Correct approach: Include selectedTimeIndex in the main zone watcher

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<template>
  <div id="map" class="w-full h-full bg-sea-blue"></div>
</template>

<style scoped>
#map {
  z-index: 1;
}

/* Global style for Leaflet marker animation */
@keyframes pulse-fast {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
:global(.animate-pulse-fast) {
  animation: pulse-fast 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
