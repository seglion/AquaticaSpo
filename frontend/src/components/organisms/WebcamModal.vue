<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import { X, Camera } from 'lucide-vue-next';
import type { MeteoGaliciaWebcam } from '../../api/webcams.service';

const props = defineProps<{
    isOpen: boolean;
    webcam: MeteoGaliciaWebcam | null;
}>();

const emit = defineEmits(['close']);

// Handle ESC key to close
const handleKeydown = (e: KeyboardEvent) => {
    if (e.key === 'Escape' && props.isOpen) {
        emit('close');
    }
};

onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
  <div v-if="isOpen && webcam" class="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 shadow-2xl">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-slate-900/80 backdrop-blur-md transition-opacity duration-300" @click="emit('close')"></div>

    <!-- Modal Content -->
    <div class="relative bg-slate-800 border border-slate-700/50 rounded-2xl overflow-hidden shadow-2xl max-w-5xl w-full flex flex-col pointer-events-auto transform transition-all duration-300 scale-100">
      
      <!-- Header -->
      <div class="px-5 py-4 flex justify-between items-center bg-slate-800 border-b border-slate-700/50">
        <div class="flex items-center gap-3">
            <div class="p-2 bg-sky-500/10 rounded-lg">
                <Camera class="w-5 h-5 text-sky-400" />
            </div>
            <div>
                <h3 class="text-lg font-semibold text-slate-100 leading-none">{{ webcam.nomeCamara }}</h3>
                <p class="text-[11px] text-slate-400 mt-1 uppercase tracking-wider font-semibold">{{ webcam.concello }}, {{ webcam.provincia }}</p>
            </div>
        </div>
        <button @click="emit('close')" class="text-slate-400 hover:text-white transition-colors p-2 rounded-xl hover:bg-slate-700 border border-transparent hover:border-slate-600 focus:outline-none focus:ring-2 focus:ring-sky-500/50">
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Image Area -->
      <div class="relative bg-black w-full flex items-center justify-center overflow-hidden" style="min-height: 50vh;">
          <img 
              :src="webcam.imaxeCamara + '?t=' + new Date().getTime()" 
              :alt="webcam.nomeCamara"
              class="w-full h-full object-contain max-h-[70vh]"
          />
          <div class="absolute bottom-4 right-4 px-3 py-1.5 bg-black/60 backdrop-blur-md rounded-lg text-sm font-mono text-slate-200 border border-white/10 shadow-lg flex items-center gap-2">
               <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
               {{ new Date(webcam.dataUltimaAct).toLocaleString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute:'2-digit'}) }}
          </div>
      </div>
      
      <!-- Footer Info -->
      <div class="px-5 py-3 bg-slate-800 text-sm text-slate-400 flex items-center justify-between border-t border-slate-700/50">
          <span class="text-xs">Fuente: MeteoGalicia (Xunta de Galicia)</span>
          <a :href="webcam.imaxeCamara" target="_blank" class="text-sky-400 hover:text-sky-300 font-medium text-xs flex items-center gap-1 transition-colors">
              Abrir imagen original 
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
          </a>
      </div>
    </div>
  </div>
</template>
