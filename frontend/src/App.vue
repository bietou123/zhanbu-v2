<script setup lang="ts">
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const nav = [
  { name: '三盘工作台', path: '/', icon: '☯', tag: 'TRIPLE' },
  { name: '七政四余', path: '/qizheng', icon: '★', tag: 'ASTRO' },
  { name: '六壬课', path: '/liuren', icon: '六', tag: 'LIUREN' },
  { name: '占卜起卦', path: '/divination', icon: '⚊', tag: 'DIVIN' },
  { name: '梅花易数', path: '/meihua', icon: '梅', tag: 'MEIHUA' },
  { name: '周公解梦', path: '/jiemeng', icon: '夢', tag: 'DREAM' },
  { name: '我的档案', path: '/profiles', icon: '⌘', tag: 'PROF' },
]
const activePath = computed(() => route.path)
</script>

<template>
  <div class="min-h-full flex flex-col md:flex-row">
    <!-- 桌面端侧栏 -->
    <aside class="hidden md:flex md:flex-col md:w-60 lg:w-64
                  bg-ink-900/70 backdrop-blur-xl
                  border-r border-cyber-400/15
                  px-4 py-6 sticky top-0 h-screen relative">
      <!-- 侧栏霓虹边线 -->
      <div class="absolute top-0 bottom-0 right-0 w-px
                  bg-gradient-to-b from-transparent via-cyber-400/40 to-transparent"></div>

      <RouterLink to="/" class="flex items-center gap-3 mb-8 group">
        <span class="seal text-base">卜</span>
        <div>
          <div class="font-kai text-xl tracking-widest"
               style="background:linear-gradient(90deg,#e07b3c,#22d3ee);-webkit-background-clip:text;background-clip:text;color:transparent;">
            詹卜
          </div>
          <div class="text-[10px] text-cyber-300/70 font-mono tracking-widest">ZHANBU · v0.2</div>
        </div>
      </RouterLink>

      <nav class="flex-1 space-y-1">
        <RouterLink v-for="n in nav" :key="n.path" :to="n.path"
          class="group flex items-center gap-3 px-3 py-2.5 rounded-xl
                 text-slate-300 hover:text-white hover:bg-ink-700/60 transition relative overflow-hidden"
          :class="{ 'bg-gradient-to-r from-cyber-500/15 via-ember-500/10 to-transparent text-white':
                    activePath === n.path }">
          <span v-if="activePath === n.path"
                class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6
                       bg-gradient-to-b from-cyber-400 to-ember-500 rounded-r shadow-glow-cyber"></span>
          <span class="font-kai w-5 text-center"
                :class="activePath === n.path ? 'text-cyber-300' : 'text-ember-400'">
            {{ n.icon }}
          </span>
          <span class="flex-1">{{ n.name }}</span>
          <span class="text-[9px] font-mono opacity-50 group-hover:opacity-100 transition">
            {{ n.tag }}
          </span>
        </RouterLink>
      </nav>

      <div class="mt-auto pt-6 text-[10px] text-cyber-300/40 border-t border-ink-600/40 font-mono space-y-0.5">
        <div>● ONLINE · 2026</div>
        <div class="text-ink-500">v0.2.0 · 国潮 + cyber</div>
      </div>
    </aside>

    <!-- 手机端顶部 -->
    <header class="md:hidden sticky top-0 z-30
                   bg-ink-900/90 backdrop-blur-xl
                   border-b border-cyber-400/20 px-4 py-3 flex items-center gap-3">
      <span class="seal text-sm">卜</span>
      <span class="font-kai text-lg tracking-widest"
            style="background:linear-gradient(90deg,#e07b3c,#22d3ee);-webkit-background-clip:text;background-clip:text;color:transparent;">
        詹卜
      </span>
      <div class="ml-auto overflow-x-auto whitespace-nowrap flex gap-1">
        <RouterLink v-for="n in nav" :key="n.path" :to="n.path"
          class="text-xs px-2 py-1 rounded-md text-slate-300 font-kai"
          :class="{ 'bg-cyber-500/30 text-white shadow-glow-cyber': activePath === n.path }">
          {{ n.icon }}
        </RouterLink>
      </div>
    </header>

    <main class="flex-1 min-w-0 px-4 md:px-8 py-6 md:py-10 max-w-[1600px] mx-auto w-full">
      <RouterView v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 250ms ease, transform 250ms ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
