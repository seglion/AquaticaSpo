import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Badge from './Badge.vue'

describe('Badge.vue', () => {
    it('renders text when passed', () => {
        const text = 'Active'
        const wrapper = mount(Badge, {
            props: { text }
        })
        expect(wrapper.text()).toMatch(text)
    })

    it('applies custom class when passed', () => {
        const customClass = 'bg-red-500'
        const wrapper = mount(Badge, {
            props: { text: 'Test', customClass }
        })
        expect(wrapper.classes()).toContain('bg-red-500')
    })
})
