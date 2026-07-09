<script setup lang="ts">
/**
 * @file SliderInput.vue
 * @description An atomic component for a range slider input, styled for the application's dark theme.
 */

/**
 * Props for the SliderInput component.
 */
export interface SliderInputProps {
  /** The minimum value of the slider */
  min?: number;
  /** The maximum value of the slider */
  max: number;
  /** The current value of the slider */
  modelValue: number;
}

const props = withDefaults(defineProps<SliderInputProps>(), {
  min: 0,
});

/**
 * Emits for the SliderInput component.
 */
const emit = defineEmits<{
  /** Emitted when the slider value changes (two-way binding for v-model) */
  (e: 'update:modelValue', val: number): void;
}>();

/**
 * TSDoc: Handle input change and emit the updated value.
 */
const handleInput = (e: Event) => {
  const target = e.target as HTMLInputElement;
  const val = parseInt(target.value, 10);
  emit('update:modelValue', val);
};
</script>

<template>
  <input 
    type="range" 
    :min="min" 
    :max="max" 
    :value="modelValue" 
    @input="handleInput"
    class="custom-slider w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-sky-500 hover:accent-sky-400 transition-all"
  />
</template>

<style scoped>
/* Custom Range Slider Styling extracted from TimeSlider */
.custom-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  height: 16px;
  width: 16px;
  border-radius: 50%;
  background: #0ea5e9; /* sky-500 */
  border: 2px solid #0f172a; /* slate-900 */
  cursor: pointer;
  box-shadow: 0 0 10px rgba(14, 165, 233, 0.5);
  margin-top: -6px; /* Necessary for older webkits */
}

.custom-slider::-webkit-slider-runnable-track {
  width: 100%;
  height: 4px;
  cursor: pointer;
  background: #334155;
  border-radius: 2px;
}
</style>
