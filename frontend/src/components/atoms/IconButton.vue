<script setup lang="ts">
/**
 * @file IconButton.vue
 * @description An atomic component for a button containing only an icon.
 */
import { type Component } from 'vue';

/**
 * Props for the IconButton component.
 */
export interface IconButtonProps {
  /** The icon component to render (e.g., from lucide-vue-next) */
  icon: Component;
  /** Extra CSS classes for the button, e.g. for color or sizing */
  customClass?: string;
  /** Extra CSS classes for the icon specifically */
  iconClass?: string;
  /** Accessibility label for screen readers */
  ariaLabel?: string;
}

const props = withDefaults(defineProps<IconButtonProps>(), {
  customClass: 'text-slate-400 hover:text-white hover:bg-slate-700 rounded-full transition-colors p-2',
  iconClass: 'w-6 h-6',
  ariaLabel: 'Icon button',
});

/**
 * Emits for the IconButton component.
 */
const emit = defineEmits<{
  /** Emitted when the user clicks the button */
  (e: 'click', event: MouseEvent): void;
}>();
</script>

<template>
  <button 
    @click="(event) => emit('click', event)" 
    :class="customClass"
    :aria-label="ariaLabel"
    type="button"
  >
    <component :is="icon" :class="iconClass" />
  </button>
</template>
