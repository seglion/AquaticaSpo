// @vitest-environment jsdom
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
// @ts-ignore
import BrandName from './BrandName.vue'

describe('BrandName.vue', () => {
    it('mounts properly', () => {
        const wrapper = mount(BrandName)
        expect(wrapper.exists()).toBe(true)
    })

    it('renders "SwellBeat" with correct styling structure', () => {
        const wrapper = mount(BrandName)
        expect(wrapper.text()).toContain('SwellBeat')
        const beatSpan = wrapper.find('span.text-brass')
        expect(beatSpan.exists()).toBe(true)
        expect(beatSpan.text()).toBe('Beat')
    })
})
