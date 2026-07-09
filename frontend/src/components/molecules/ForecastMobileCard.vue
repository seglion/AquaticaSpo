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
  /** Cota de remonte Ru2% (runup + marea) en metros */
  cotaRu2p?: number;
  /** Cota de remonte Ru1% (runup + marea) en metros */
  cotaRu1p?: number;
}

/**
 * Interface mapping a model name (e.g. 'ewam') to its associated forecast data for this time row.
 */
export interface ForecastRowData {
  time: string;
  /** Nivel de marea (m) para este instante, común a todos los modelos */
  tide?: number;
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
  /** 
   * A helper function to color-code wave height values dynamically. 
   * Returns a Tailwind class string.
   */
  getBgColorHelper: (height?: number) => string;
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
          <div class="rounded-md p-1.5 flex flex-col items-center justify-center transition-colors" 
               :class="getBgColorHelper((row[model] as ForecastRowModelData).height) || 'bg-slate-700 text-slate-300'">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Hs (m)</span>
            <span class="font-bold mt-0.5">{{ (row[model] as ForecastRowModelData).height?.toFixed(2) ?? '-' }}</span>
          </div>
          
          <!-- Tp (Peak Period) -->
          <div class="rounded-md p-1.5 flex flex-col items-center justify-center transition-colors" 
               :class="getBgColorHelper((row[model] as ForecastRowModelData).height) || 'bg-slate-700 text-slate-300'">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Tp (s)</span>
            <span class="font-bold mt-0.5">{{ (row[model] as ForecastRowModelData).period?.toFixed(1) ?? '-' }}</span>
          </div>
          
          <!-- Dir (Direction) -->
          <div class="rounded-md p-1.5 flex flex-col items-center justify-center transition-colors"
               :class="getBgColorHelper((row[model] as ForecastRowModelData).height) || 'bg-slate-700 text-slate-300'">
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

        <!-- Cota de remonte (runup + marea): valor de diseño para la zona -->
        <div class="grid grid-cols-2 gap-2 text-center text-sm mt-2">
          <div class="rounded-md p-1.5 flex flex-col items-center justify-center bg-violet-950/40 text-violet-200 border border-violet-800/40">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Cota Ru2% (m)</span>
            <span class="font-bold mt-0.5">{{ (row[model] as ForecastRowModelData).cotaRu2p?.toFixed(2) ?? '-' }}</span>
          </div>
          <div class="rounded-md p-1.5 flex flex-col items-center justify-center bg-violet-950/25 text-violet-300/90 border border-violet-800/30">
            <span class="text-[9px] opacity-80 uppercase font-semibold">Cota Ru1% (m)</span>
            <span class="font-bold mt-0.5">{{ (row[model] as ForecastRowModelData).cotaRu1p?.toFixed(2) ?? '-' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
