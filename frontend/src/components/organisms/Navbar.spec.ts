// @vitest-environment jsdom
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
// @ts-ignore
import Navbar from './Navbar.vue'
import BrandIdentity from '../molecules/BrandIdentity.vue'

describe('Navbar.vue', () => {
    it('mounts properly', () => {
        const wrapper = mount(Navbar)
        expect(wrapper.exists()).toBe(true)
    })

    it('renders a semantic nav element', () => {
        const wrapper = mount(Navbar)
        expect(wrapper.find('nav').exists()).toBe(true)
    })

    it('contains the BrandIdentity molecule', () => {
        const wrapper = mount(Navbar)
        expect(wrapper.findComponent(BrandIdentity).exists()).toBe(true)
    })
})
