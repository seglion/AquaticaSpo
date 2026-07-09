import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import IconButton from './IconButton.vue'
import { X } from 'lucide-vue-next'

describe('IconButton.vue', () => {
    it('renders without errors', () => {
        const wrapper = mount(IconButton, {
            props: { icon: X }
        })
        expect(wrapper.exists()).toBe(true)
    })

    it('emits click event when clicked', async () => {
        const wrapper = mount(IconButton, {
            props: { icon: X }
        })
        await wrapper.trigger('click')
        expect(wrapper.emitted()).toHaveProperty('click')
    })
})
