<template>
  <div class="min-h-screen flex items-center justify-center relative bg-slate-900 py-12 px-4 sm:px-4 lg:px-4 overflow-hidden">
    
    <!-- Background Image -->
    <div class="absolute inset-0 z-0">
      <img 
        src="https://images.unsplash.com/photo-1505118380757-91f5f5632de0?q=80&w=2560&auto=format&fit=crop" 
        alt="Ocean Waves" 
        class="w-full h-full object-cover"
      />
      <!-- Dark gradient overlay for better contrast -->
      <div class="absolute inset-0 bg-gradient-to-br from-slate-900/90 via-slate-900/70 to-slate-900/95 backdrop-blur-[2px]"></div>
    </div>

    <!-- Main Content Box -->
    <div class="relative z-10 max-w-md w-full space-y-4">
        <router-view></router-view>
    </div>

  </div>
</template>
