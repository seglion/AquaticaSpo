<script setup lang="ts">
/**
 * @file Badge.vue
 * @description An atomic component for displaying a small badge or label.
 */

/**
 * Props for the Badge component.
 */
export interface BadgeProps {
  /** The text content of the badge. */
  text: string;
  /** Optional custom Tailwind CSS classes for background, text color, etc. Default is a dark slate style. */
  customClass?: string;
}

const props = withDefaults(defineProps<BadgeProps>(), {
  customClass: 'bg-slate-800 text-white',
});
</script>

<template>
  <span 
    class="font-mono text-sm font-bold px-2 py-1 rounded inline-block"
    :class="customClass"
  >
    {{ text }}
  </span>
</template>
