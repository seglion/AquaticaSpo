<script setup lang="ts">
/**
 * @file SidebarItem.vue
 * @description A molecular component for a single navigation item in a Sidebar.
 *              It includes an icon and text, and optionally acts as an active link.
 */
import { type Component } from 'vue';

/**
 * Props for the SidebarItem component.
 */
export interface SidebarItemProps {
  /** The icon to display alongside the text */
  icon: Component;
  /** The text label of the sidebar item */
  label: string;
  /** Is this item currently the active view? */
  isActive?: boolean;
}

const props = withDefaults(defineProps<SidebarItemProps>(), {
  isActive: false,
});
</script>

<template>
  <div 
    class="flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors cursor-pointer"
    :class="[
      isActive 
        ? 'bg-sky-500/10 text-sky-400 font-medium' 
        : 'text-slate-400 hover:bg-slate-800 hover:text-white'
    ]"
  >
    <component :is="icon" class="w-5 h-5 flex-shrink-0" />
    <span class="truncate">{{ label }}</span>
  </div>
</template>
