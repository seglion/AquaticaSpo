// @vitest-environment jsdom
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
// @ts-ignore
import AppLogo from './AppLogo.vue'

describe('AppLogo.vue', () => {
    it('mounts properly', () => {
        const wrapper = mount(AppLogo)
        expect(wrapper.exists()).toBe(true)
    })

    it('renders the logo image with correct src and alt', () => {
        const wrapper = mount(AppLogo)
        const img = wrapper.find('img')
        expect(img.exists()).toBe(true)
        expect(img.attributes('alt')).toBe('SwellBeat Logo')
        expect(img.attributes('src')).toContain('cropped-SBlogoSite-1-1.png')
    })
})
