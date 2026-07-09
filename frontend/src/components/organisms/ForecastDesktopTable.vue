<script setup lang="ts">
/**
 * @file ForecastDesktopTable.vue
 * @description An organism component representing the large data table for desktop views.
 */
import { ArrowUp } from 'lucide-vue-next';
import type { ForecastRowData, ForecastRowModelData } from '../molecules/ForecastMobileCard.vue';

export interface ForecastDesktopTableProps {
  /** Array of formatted row data */
  hourlyData: ForecastRowData[];
  /** List of model names */
  models: string[];
  /** Helper function for cell background colors */
  getBgColorHelper: (height?: number) => string;
  /** Helper function to format dates */
  formatDateHelper: (iso: string) => string;
}

defineProps<ForecastDesktopTableProps>();
</script>

<template>
  <table class="w-full border-collapse text-left text-sm hidden md:table">
    <thead class="bg-slate-800 text-slate-300 sticky top-0 z-10 shadow-md">
      <tr>
        <th class="p-3 border-b border-slate-700 font-medium min-w-[150px] sticky left-0 bg-slate-800 z-20">Fecha / Hora</th>
        <th class="p-3 border-b border-slate-700 font-medium text-center border-l border-slate-700 min-w-[90px]">
          <span class="uppercase tracking-wider text-xs font-bold text-cyan-300">Marea</span>
        </th>
        <!-- Group headers by Model -->
        <th v-for="model in models" :key="model" class="p-3 border-b border-slate-700 font-medium text-center border-l border-slate-700" colspan="5">
          <span class="uppercase tracking-wider text-xs font-bold text-sky-400">{{ model }}</span>
        </th>
      </tr>
      <tr>
        <th class="p-2 border-b border-slate-750 sticky left-0 bg-slate-800 z-20"></th>
        <th class="p-2 border-b border-slate-750 text-center text-xs text-slate-400 border-l border-slate-800">(m)</th>
        <template v-for="model in models" :key="model + '_sub'">
          <th class="p-2 border-b border-slate-750 text-center text-xs text-slate-400 border-l border-slate-800">Hs (m)</th>
          <th class="p-2 border-b border-slate-750 text-center text-xs text-slate-400">Tp (s)</th>
          <th class="p-2 border-b border-slate-750 text-center text-xs text-slate-400">Dir</th>
          <th class="p-2 border-b border-slate-750 text-center text-xs text-violet-300 border-l border-slate-800">Cota Ru2% (m)</th>
          <th class="p-2 border-b border-slate-750 text-center text-xs text-violet-300/80">Cota Ru1% (m)</th>
        </template>
      </tr>
    </thead>
    <tbody class="divide-y divide-slate-800">
      <tr v-for="(row, idx) in hourlyData" :key="idx" class="hover:bg-slate-800/30 transition-colors group">
        <td class="p-3 border-r border-slate-800 text-slate-300 font-mono whitespace-nowrap sticky left-0 bg-slate-900 group-hover:bg-slate-800/30">
          {{ formatDateHelper(row.time) }}
        </td>
        <td class="p-2 text-center border-l border-r border-slate-800 text-cyan-200 font-medium">
          {{ (row.tide as number | undefined)?.toFixed(2) ?? '-' }}
        </td>
        <template v-for="model in models" :key="model + '_' + idx">
          <!-- Hs -->
          <td class="p-2 text-center border-l border-slate-800/50 font-medium" 
              :class="getBgColorHelper((row[model] as ForecastRowModelData).height)">
            {{ (row[model] as ForecastRowModelData).height?.toFixed(2) }}
          </td>
          <!-- Tp -->
          <td class="p-2 text-center"
              :class="getBgColorHelper((row[model] as ForecastRowModelData).height)">
            {{ (row[model] as ForecastRowModelData).period?.toFixed(1) }}
          </td>
          <!-- Dir -->
          <td class="p-2 text-center"
              :class="getBgColorHelper((row[model] as ForecastRowModelData).height)">
            <div class="flex items-center justify-center" v-if="(row[model] as ForecastRowModelData).direction !== undefined">
              <ArrowUp class="w-4 h-4 opacity-70 transition-transform" :style="{ transform: `rotate(${((row[model] as ForecastRowModelData).direction ?? 0) + 180}deg)` }" />
            </div>
            <span v-else>-</span>
          </td>
          <!-- Cota de remonte Ru2% (runup + marea) -->
          <td class="p-2 text-center border-l border-slate-800 text-violet-200 font-medium bg-violet-950/20">
            {{ (row[model] as ForecastRowModelData).cotaRu2p?.toFixed(2) ?? '-' }}
          </td>
          <!-- Cota de remonte Ru1% -->
          <td class="p-2 text-center text-violet-300/90 bg-violet-950/10">
            {{ (row[model] as ForecastRowModelData).cotaRu1p?.toFixed(2) ?? '-' }}
          </td>
        </template>
      </tr>
    </tbody>
  </table>
</template>
