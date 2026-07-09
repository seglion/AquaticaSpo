<script setup lang="ts">
/**
 * @file ForecastMobileList.vue
 * @description An organism component representing the vertically stacked list of mobile cards for the forecast view.
 */
import ForecastMobileCard from '../molecules/ForecastMobileCard.vue';
import type { ForecastRowData } from '../molecules/ForecastMobileCard.vue';

export interface ForecastMobileListProps {
  /** Array of formatted row data */
  hourlyData: ForecastRowData[];
  /** List of model names */
  models: string[];
  /** Helper function for cell background colors */
  getBgColorHelper: (height?: number) => string;
  /** Helper function to format dates */
  formatDateHelper: (iso: string) => string;
}

defineProps<ForecastMobileListProps>();
</script>

<template>
  <div class="md:hidden flex flex-col space-y-4 p-4">
    <ForecastMobileCard 
      v-for="(row, idx) in hourlyData" 
      :key="'mob_' + idx"
      :row="row"
      :models="models"
      :getBgColorHelper="getBgColorHelper"
      :formatDateHelper="formatDateHelper"
    />
  </div>
</template>
