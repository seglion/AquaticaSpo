import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '../api/client'
import type { Contract, ForecastSystem, Port, HindcastPoint, DownloadedData, ForecastZone } from '../types'
import { parseUTCDate } from '../utils/dateFormatter'

export const useForecastStore = defineStore('forecast', () => {
    const systems = ref<ForecastSystem[]>([])
    const loading = ref(false)
    const error = ref<string | null>(null)

    async function fetchSystems() {
        loading.value = true
        error.value = null
        systems.value = []

        try {
            // 1. Get Contracts
            console.log('Fetching contracts...')
            const contractsResponse = await apiClient.get<Contract[]>('/contracts/my')
            const contracts = contractsResponse.data
            console.log('Contracts fetched:', contracts)

            if (!contracts || contracts.length === 0) {
                console.warn('No contracts found for user')
                systems.value = []
                return
            }

            // 2. For each contract, get associated system
            // Parallel requests
            console.log('Fetching systems for contracts:', contracts.map(c => c.id))
            const systemPromises = contracts.map(contract =>
                apiClient.get<ForecastSystem>(`/forecast-systems/by-contract/${contract.id}`)
                    .then(res => {
                        console.log(`System fetched for contract ${contract.id}:`, res.data)
                        return res.data
                    })
                    .catch(err => {
                        console.warn(`Failed to fetch system for contract ${contract.id}`, err)
                        return null
                    })
            )

            const results = await Promise.all(systemPromises)

            // Filter out nulls (failed requests)
            const validSystems = results.filter((s): s is ForecastSystem => s !== null)
            console.log('Valid systems:', validSystems)

            // Remove duplicates if any (though logic suggests 1 system per contract usually, or unique IDs)
            // Using a Map by ID to ensure uniqueness
            const uniqueSystems = Array.from(new Map(validSystems.map(s => [s.id, s])).values())

            systems.value = uniqueSystems
            console.log('Systems set in store:', systems.value)

        } catch (e: any) {
            console.error('Error fetching systems:', e)
            error.value = `Failed to load forecast systems: ${e.message || e}`
        } finally {
            loading.value = false
        }
    }

    const selectedPort = ref<Port | null>(null)
    const selectedHindcastPoint = ref<HindcastPoint | null>(null)
    const selectedDownloadedData = ref<DownloadedData | null>(null)
    const selectedTimeIndex = ref(0)
    const forecastZones = ref<ForecastZone[]>([])
    // Store data for each zone: zoneId -> DownloadedData
    const forecastZonesData = ref<Record<number, DownloadedData>>({})
    const selectedZoneData = ref<DownloadedData | null>(null)
    const selectedZoneId = ref<number | null>(null)

    async function selectSystem(systemId: number) {
        const system = systems.value.find(s => s.id === systemId)
        if (!system) return

        loading.value = true
        // Reset previous selection to avoid mixing data during load
        selectedPort.value = null
        selectedHindcastPoint.value = null
        selectedDownloadedData.value = null
        selectedTimeIndex.value = 0
        forecastZones.value = []
        forecastZonesData.value = {}
        selectedZoneData.value = null
        selectedZoneId.value = null

        try {
            console.log(`Fetching data for system ${systemId}...`)

            // Execute requests in parallel
            // We use allSettled for downloadedData because it might not exist yet (404), 
            // and we don't want to fail the whole operation if just the data is missing.
            const [portRes, hindcastRes] = await Promise.all([
                apiClient.get<Port>(`/ports/${system.port_id}`),
                apiClient.get<HindcastPoint>(`/hindcast-points/${system.hindcast_point_id}`)
            ])

            selectedPort.value = portRes.data
            selectedHindcastPoint.value = hindcastRes.data

            // Fetch downloaded data separately to handle 404 gracefully
            try {
                const dataRes = await apiClient.get<DownloadedData>(`/downloaded-data/latest/by-point/${system.hindcast_point_id}`)
                selectedDownloadedData.value = dataRes.data
                console.log('Downloaded Data fetched:', selectedDownloadedData.value)

                // Auto-sync Time Slider to the closest current time
                const data = dataRes.data?.data
                const hourly = data?.hourly || data

                if (hourly && hourly.time && hourly.time.length > 0) {
                    const now = new Date().getTime()
                    let closestIndex = 0
                    let minDiff = Infinity

                    for (let i = 0; i < hourly.time.length; i++) {
                        const timeVal = parseUTCDate(hourly.time[i]).getTime()
                        const diff = Math.abs(timeVal - now)
                        if (diff < minDiff) {
                            minDiff = diff
                            closestIndex = i
                        }
                    }
                    selectedTimeIndex.value = closestIndex
                    console.log(`Synced time slider to index ${closestIndex} - ${hourly.time[closestIndex]}`)
                }

            } catch (err: any) {
                // Ignore 404 for data, log others
                if (!err.response || err.response.status !== 404) {
                    console.error('Error fetching downloaded data:', err)
                } else {
                    console.warn('No downloaded data found.')
                }
            }

            // Fetch Forecast Zones and their data
            try {
                const zonesRes = await apiClient.get<ForecastZone[]>(`/forecast-zones/by-system/${systemId}`)
                forecastZones.value = zonesRes.data
                console.log('Forecast Zones fetched:', forecastZones.value)

                // Fetch data for ALL zones in parallel
                // Endpoint: /forecast-results/latest-by-zone/{zone_id}
                const zoneDataPromises = forecastZones.value.map(zone =>
                    apiClient.get<any>(`/forecast-results/latest-by-zone/${zone.id}`)
                        .then(res => {
                            // Normalize ForecastSystemResultResponse to DownloadedData format
                            const payload = res.data;
                            const normalizedData: DownloadedData = {
                                id: payload.id,
                                point_id: payload.forecast_zone_id,
                                downloaded_at: payload.execution_date, // Map execution_date to downloaded_at for UI
                                data: payload.result_data // Map result_data to data
                            };
                            return { id: zone.id, data: normalizedData };
                        })
                        .catch(err => {
                            console.warn(`No data for zone ${zone.id}`, err)
                            return null
                        })
                )


                const zoneDataResults = await Promise.all(zoneDataPromises)

                const newDataMap: Record<number, DownloadedData> = {}
                zoneDataResults.forEach(result => {
                    if (result) {
                        newDataMap[result.id] = result.data
                    }
                })
                forecastZonesData.value = newDataMap
                console.log('Forecast Zones Data fetched:', forecastZonesData.value)

            } catch (err) {
                console.warn('Failed to fetch forecast zones:', err)
            }

            console.log('Port fetched:', selectedPort.value)
            console.log('Hindcast Point fetched:', selectedHindcastPoint.value)

        } catch (e: any) {
            console.error('Error fetching system details:', e)
            error.value = `Error loading details: ${e.message || e}`
        } finally {
            loading.value = false
        }
    }

    return {
        systems,
        selectedPort,
        selectedHindcastPoint,
        selectedDownloadedData,
        selectedTimeIndex,
        forecastZones,
        forecastZonesData,
        selectedZoneData,
        selectedZoneId,
        loading,
        error,
        fetchSystems,
        selectSystem
    }
})
