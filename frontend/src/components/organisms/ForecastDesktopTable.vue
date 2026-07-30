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
  /** Helper function for cota cell background colors */
  getCotaColorHelper: (cotaValue?: number) => string;
  /** Helper function for wind cell background colors */
  getWindColorHelper: (speed?: number) => string;
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
        <!-- Wind column group -->
        <th class="p-3 border-b border-slate-700 font-medium text-center border-l border-slate-700" colspan="3">
          <span class="uppercase tracking-wider text-xs font-bold text-emerald-400">Viento</span>
        </th>
      </tr>
      <tr>
        <th class="p-2 border-b border-slate-750 sticky left-0 bg-slate-800 z-20"></th>
        <th class="p-2 border-b border-slate-750 text-center text-xs text-slate-400 border-l border-slate-800">(m)</th>
        <template v-for="model in models" :key="model + '_sub'">
          <th class="p-2 border-b border-slate-750 text-center text-xs text-slate-400 border-l border-slate-800">Hs (m)</th>
          <th class="p-2 border-b border-slate-750 text-center text-xs text-slate-400">Tp (s)</th>
          <th class="p-2 border-b border-slate-750 text-center text-xs text-slate-400">Dir</th>
          <th class="p-2 border-b border-slate-750 text-center text-xs text-violet-300 border-l border-slate-800">Cota (m)</th>
          <th class="p-2 border-b border-slate-750 text-center text-xs text-amber-300">Q (l/s/m)</th>
        </template>
        <!-- Wind sub-headers -->
        <th class="p-2 border-b border-slate-750 text-center text-xs text-emerald-300 border-l border-slate-800">Vel (km/h)</th>
        <th class="p-2 border-b border-slate-750 text-center text-xs text-emerald-300/80">Ráf (km/h)</th>
        <th class="p-2 border-b border-slate-750 text-center text-xs text-emerald-300/80">Dir</th>
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
          <td class="p-2 text-center border-l border-slate-800/50 font-medium text-slate-300 bg-slate-800/30">
            {{ (row[model] as ForecastRowModelData).height?.toFixed(2) }}
          </td>
          <!-- Tp -->
          <td class="p-2 text-center text-slate-300 bg-slate-800/20">
            {{ (row[model] as ForecastRowModelData).period?.toFixed(1) }}
          </td>
          <!-- Dir -->
          <td class="p-2 text-center text-slate-300 bg-slate-800/10">
            <div class="flex items-center justify-center" v-if="(row[model] as ForecastRowModelData).direction !== undefined">
              <ArrowUp class="w-4 h-4 opacity-70 transition-transform" :style="{ transform: `rotate(${((row[model] as ForecastRowModelData).direction ?? 0) + 180}deg)` }" />
            </div>
            <span v-else>-</span>
          </td>
          <!-- Cota de remonte (runup + marea) -->
          <td class="p-2 text-center border-l border-slate-800 font-medium"
              :class="getCotaColorHelper((row[model] as ForecastRowModelData).cotaRu2p) || 'text-violet-200 bg-violet-950/20'">
            {{ (row[model] as ForecastRowModelData).cotaRu2p?.toFixed(2) ?? '-' }}
          </td>
          <!-- Caudal de rebase (overtopping) -->
          <td class="p-2 text-center font-medium"
              :class="((row[model] as ForecastRowModelData).caudalRebase ?? 0) > 10 ? 'bg-red-600 text-red-100' : 'bg-amber-950/30 text-amber-200'">
            {{ (row[model] as ForecastRowModelData).caudalRebase?.toFixed(2) ?? '-' }}
          </td>
        </template>
        <!-- Wind data cells -->
        <td class="p-2 text-center border-l border-slate-800 font-medium"
            :class="getWindColorHelper(row.windSpeed as number | undefined)">
          {{ (row.windSpeed as number | undefined)?.toFixed(1) ?? '-' }}
        </td>
        <td class="p-2 text-center"
            :class="getWindColorHelper(row.windGusts as number | undefined)">
          {{ (row.windGusts as number | undefined)?.toFixed(1) ?? '-' }}
        </td>
        <td class="p-2 text-center text-emerald-200/80 bg-emerald-950/10">
          <div class="flex items-center justify-center" v-if="row.windDirection !== undefined">
            <ArrowUp class="w-4 h-4 opacity-70 transition-transform" :style="{ transform: `rotate(${(row.windDirection as number) + 180}deg)` }" />
          </div>
          <span v-else>-</span>
        </td>
      </tr>
    </tbody>
  </table>
</template>
