<script setup lang="ts">
/**
 * @file ForecastMobileCard.vue
 * @description A molecular component representing a single row of forecast data
 *              (one specific timestamp) rendered as a vertical card for mobile resolutions.
 */
import { ArrowUp } from 'lucide-vue-next';

/**
 * A mapped index of data per model for a specific timestamp.
 */
export interface ForecastRowModelData {
  /** Significant wave height in meters */
  height?: number;
  /** Peak wave period in seconds */
  period?: number;
  /** Peak wave direction in degrees */
  direction?: number;
  /** Cota de remonte (runup + marea) en metros */
  cotaRu2p?: number;
  /** Caudal de rebase (overtopping) en l/s/m */
  caudalRebase?: number;
}

/**
 * Interface mapping a model name (e.g. 'ewam') to its associated forecast data for this time row.
 */
export interface ForecastRowData {
  time: string;
  /** Nivel de marea (m) para este instante, común a todos los modelos */
  tide?: number;
  /** Velocidad del viento a 10m (km/h) */
  windSpeed?: number;
  /** Ráfaga de viento a 10m (km/h) */
  windGusts?: number;
  /** Dirección del viento a 10m (grados) */
  windDirection?: number;
  [modelName: string]: ForecastRowModelData | string | number | undefined;
}

/**
 * Props for the ForecastMobileCard component.
 */
export interface ForecastMobileCardProps {
  /** The data for a single timeframe across multiple models */
  row: ForecastRowData;
  /** A list of valid model names to render (e.g., ['ewam', 'ncep_gfswave025']) */
  models: string[];
  /** Helper function for cota cell background colors */
  getCotaColorHelper: (cotaValue?: number) => string;
  /** Helper function for wind cell background colors */
  getWindColorHelper: (speed?: number) => string;
  /**
   * Formats the ISO UTC timestamp into a human readable local string.
   */
  formatDateHelper: (iso: string) => string;
}

const props = defineProps<ForecastMobileCardProps>();
</script>

<template>
  <div class="bg-slate-800 rounded-lg p-3 shadow-md border border-slate-700">
    <div class="font-mono text-slate-200 font-semibold mb-3 border-b border-slate-700/80 pb-2 text-center flex items-center justify-center gap-3">
      <span>{{ formatDateHelper(row.time) }}</span>
      <span v-if="row.tide !== undefined" class="text-xs font-normal text-cyan-300">
        Marea: {{ (row.tide as number).toFixed(2) }} m
      </span>
    </div>
    
    <div class="space-y-4">
      <div v-for="model in models" :key="model">
        <h4 class="text-[11px] font-bold text-sky-400 uppercase tracking-wide mb-1.5 text-center">{{ model }}</h4>
        <div class="grid grid-cols-3 gap-2 text-center text-sm">
          
          <!-- Hs (Significant Height) -->
          <div class="rounded-md p-1.5 flex flex-col items-center justify-center bg-slate-700 text-slate-300">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Hs (m)</span>
            <span class="font-bold mt-0.5">{{ (row[model] as ForecastRowModelData).height?.toFixed(2) ?? '-' }}</span>
          </div>
          
          <!-- Tp (Peak Period) -->
          <div class="rounded-md p-1.5 flex flex-col items-center justify-center bg-slate-700 text-slate-300">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Tp (s)</span>
            <span class="font-bold mt-0.5">{{ (row[model] as ForecastRowModelData).period?.toFixed(1) ?? '-' }}</span>
          </div>
          
          <!-- Dir (Direction) -->
          <div class="rounded-md p-1.5 flex flex-col items-center justify-center bg-slate-700 text-slate-300">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Dir</span>
            <div class="mt-0.5 flex justify-center w-full" v-if="(row[model] as ForecastRowModelData).direction !== undefined">
              <ArrowUp
                class="w-4 h-4 opacity-90 transition-transform"
                :style="{ transform: `rotate(${((row[model] as ForecastRowModelData).direction ?? 0) + 180}deg)` }"
              />
            </div>
            <span v-else class="mt-0.5">-</span>
          </div>

        </div>

        <!-- Cota de remonte y caudal de rebase -->
        <div class="grid grid-cols-2 gap-2 text-center text-sm mt-2">
          <div class="rounded-md p-1.5 flex flex-col items-center justify-center border"
               :class="getCotaColorHelper((row[model] as ForecastRowModelData).cotaRu2p) || 'bg-violet-950/40 text-violet-200 border-violet-800/40'">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Cota (m)</span>
            <span class="font-bold mt-0.5">{{ (row[model] as ForecastRowModelData).cotaRu2p?.toFixed(2) ?? '-' }}</span>
          </div>
          <div class="rounded-md p-1.5 flex flex-col items-center justify-center border"
               :class="((row[model] as ForecastRowModelData).caudalRebase ?? 0) > 10 ? 'bg-red-600 text-red-100' : 'bg-amber-950/30 text-amber-200 border-amber-800/30'">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Q (l/s/m)</span>
            <span class="font-bold mt-0.5">{{ (row[model] as ForecastRowModelData).caudalRebase?.toFixed(2) ?? '-' }}</span>
          </div>
        </div>
      </div>

      <!-- Wind Section -->
      <div v-if="row.windSpeed !== undefined || row.windGusts !== undefined || row.windDirection !== undefined" class="mt-3 pt-3 border-t border-slate-700/60">
        <h4 class="text-[11px] font-bold text-emerald-400 uppercase tracking-wide mb-1.5 text-center">Viento</h4>
        <div class="grid grid-cols-3 gap-2 text-center text-sm">
          <div v-if="row.windSpeed !== undefined" class="rounded-md p-1.5 flex flex-col items-center justify-center border"
               :class="getWindColorHelper(row.windSpeed as number) || 'bg-emerald-950/40 text-emerald-200 border-emerald-800/40'">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Vel (km/h)</span>
            <span class="font-bold mt-0.5">{{ (row.windSpeed as number).toFixed(1) }}</span>
          </div>
          <div v-if="row.windGusts !== undefined" class="rounded-md p-1.5 flex flex-col items-center justify-center border"
               :class="getWindColorHelper(row.windGusts as number) || 'bg-emerald-950/40 text-emerald-200 border-emerald-800/40'">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Ráf (km/h)</span>
            <span class="font-bold mt-0.5">{{ (row.windGusts as number).toFixed(1) }}</span>
          </div>
          <div v-if="row.windDirection !== undefined" class="rounded-md p-1.5 flex flex-col items-center justify-center bg-emerald-950/40 text-emerald-200 border border-emerald-800/40">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Dir</span>
            <div class="mt-0.5 flex justify-center">
              <ArrowUp class="w-4 h-4 opacity-90 transition-transform" :style="{ transform: `rotate(${(row.windDirection as number) + 180}deg)` }" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
