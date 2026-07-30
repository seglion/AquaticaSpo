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
  /** Helper function for cota cell background colors */
  getCotaColorHelper: (cotaValue?: number) => string;
  /** Helper function for wind cell background colors */
  getWindColorHelper: (speed?: number) => string;
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
      :getCotaColorHelper="getCotaColorHelper"
      :getWindColorHelper="getWindColorHelper"
      :formatDateHelper="formatDateHelper"
    />
  </div>
</template>
