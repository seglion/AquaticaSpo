// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import * as L from 'leaflet'
import { nextTick } from 'vue'
// @ts-ignore
import MapContainer from './MapContainer.vue'

vi.mock('leaflet', () => {
    const mockLayer = {
        addTo: vi.fn().mockReturnThis(),
    }
    const mockWms = vi.fn().mockReturnValue(mockLayer)
    const mockTileLayer = vi.fn().mockReturnValue(mockLayer)
    // @ts-ignore
    mockTileLayer.wms = mockWms

    return {
        map: vi.fn().mockReturnValue({
            setView: vi.fn((_latlng, zoom) => {
                expect(zoom).toBe(6)
                return {
                    remove: vi.fn(),
                    setView: vi.fn().mockReturnThis(),
                }
            }),
            remove: vi.fn(),
        }),
        tileLayer: mockTileLayer
    }
})

describe('MapContainer.vue', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('mounts properly and initializes leaflet map', async () => {
        const wrapper = mount(MapContainer)
        await nextTick()

        expect(wrapper.exists()).toBe(true)
        expect(L.map).toHaveBeenCalledWith('map', expect.any(Object))
    })

    it('adds ESRI World Imagery XYZ layer on mount', async () => {
        mount(MapContainer)
        await nextTick()

        expect(L.tileLayer).toHaveBeenCalledWith(
            expect.stringContaining('server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile'),
            expect.objectContaining({
                attribution: expect.stringContaining('Esri')
            })
        )
    })
})
