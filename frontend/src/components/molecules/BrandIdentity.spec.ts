// @vitest-environment jsdom
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BrandIdentity from './BrandIdentity.vue'
import AppLogo from '../atoms/AppLogo.vue'
import BrandName from '../atoms/BrandName.vue'

describe('BrandIdentity.vue', () => {
    it('mounts properly', () => {
        const wrapper = mount(BrandIdentity)
        expect(wrapper.exists()).toBe(true)
    })

    it('contains AppLogo atom', () => {
        const wrapper = mount(BrandIdentity)
        expect(wrapper.findComponent(AppLogo).exists()).toBe(true)
    })

    it('contains BrandName atom', () => {
        const wrapper = mount(BrandIdentity)
        expect(wrapper.findComponent(BrandName).exists()).toBe(true)
    })
})
