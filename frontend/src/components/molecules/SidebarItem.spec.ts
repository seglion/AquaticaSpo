import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SidebarItem from './SidebarItem.vue'
import { Activity } from 'lucide-vue-next'

describe('SidebarItem.vue', () => {
    it('renders text label', () => {
        const label = 'My System'
        const wrapper = mount(SidebarItem, {
            props: { icon: Activity, label }
        })
        expect(wrapper.text()).toContain(label)
    })

    it('applies active styling when isActive is true', () => {
        const wrapper = mount(SidebarItem, {
            props: { icon: Activity, label: 'Test', isActive: true }
        })
        expect(wrapper.classes()).toContain('bg-sky-500/10')
    })
})
