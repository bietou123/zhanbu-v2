<script setup lang="ts">
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()
const nav = [
  { name: '三盘工作台', path: '/', icon: '☯' },
  { name: '七政四余', path: '/qizheng', icon: '★' },
  { name: '六壬课', path: '/liuren', icon: '六' },
  { name: '占卜起卦', path: '/divination', icon: '⚊' },
  { name: '梅花易数', path: '/meihua', icon: '梅' },
  { name: '周公解梦', path: '/jiemeng', icon: '夢' },
  { name: '我的档案', path: '/profiles', icon: '⌘' },
]
const activePath = computed(() => route.path)
</script>

<template>
  <div class="min-h-full flex flex-col md:flex-row">
    <!-- 桌面端：左侧固定侧边栏 -->
    <aside class="hidden md:flex md:flex-col md:w-56 lg:w-64
                  bg-ink-800/80 backdrop-blur-md
                  border-r border-ink-600/60
                  px-4 py-6 sticky top-0 h-screen">
      <RouterLink to="/" class="flex items-center gap-3 mb-8 group">
        <span class="seal text-base">卜</span>
        <div>
          <div class="font-kai text-xl text-ember-500 tracking-widest">詹卜</div>
          <div class="text-xs text-ink-500">Zhanbu · 玄学平台</div>
        </div>
      </RouterLink>
      <nav class="flex-1 space-y-1">
        <RouterLink v-for="n in nav" :key="n.path" :to="n.path"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl
                 text-slate-300 hover:text-white hover:bg-ink-700/60 transition"
          :class="{ 'bg-gradient-to-r from-ember-500/20 to-transparent text-ember-300 border-l-2 border-ember-500':
                    activePath === n.path }">
          <span class="font-kai w-5 text-center text-ember-400">{{ n.icon }}</span>
          <span>{{ n.name }}</span>
        </RouterLink>
      </nav>
      <div class="mt-auto pt-6 text-xs text-ink-500 border-t border-ink-600/40">
        v0.1.0 · 2026
      </div>
    </aside>

    <!-- 手机端：顶部紧凑导航 -->
    <header class="md:hidden sticky top-0 z-30
                   bg-ink-800/90 backdrop-blur-md
                   border-b border-ink-600/60 px-4 py-3 flex items-center gap-3">
      <span class="seal text-sm">卜</span>
      <span class="font-kai text-lg text-ember-500 tracking-widest">詹卜</span>
      <div class="ml-auto overflow-x-auto whitespace-nowrap flex gap-1">
        <RouterLink v-for="n in nav" :key="n.path" :to="n.path"
          class="text-xs px-2 py-1 rounded-md text-slate-300"
          :class="{ 'bg-ember-500/30 text-white': activePath === n.path }">
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
  transition: opacity 200ms ease, transform 200ms ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
