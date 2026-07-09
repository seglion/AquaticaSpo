<script setup lang="ts">
/**
 * @file ModalHeader.vue
 * @description A molecular component representing the top header of a modal,
 *              complete with a main title, optional subtitles, and a close button.
 */
import { X } from 'lucide-vue-next';
import IconButton from '../atoms/IconButton.vue';

/**
 * Props for the ModalHeader component.
 */
export interface ModalHeaderProps {
  /** The main title of the modal */
  title: string;
}

const props = defineProps<ModalHeaderProps>();

/**
 * Emits for the ModalHeader component.
 */
const emit = defineEmits<{
  /** Emitted when the close button is clicked */
  (e: 'close'): void;
}>();
</script>

<template>
  <div class="flex items-center justify-between px-6 py-4 border-b border-slate-700 bg-slate-800/50">
    <div>
      <h2 class="text-xl font-semibold text-white">{{ title }}</h2>
      <!-- Default slot for rendering dynamic subtitles (like Zone info or downloaded time) -->
      <slot name="subtitle"></slot>
    </div>
    
    <div class="flex items-center gap-3">
      <slot name="actions"></slot>
      <IconButton
        :icon="X"
        ariaLabel="Close modal"
        @click="emit('close')"
      />
    </div>
  </div>
</template>
