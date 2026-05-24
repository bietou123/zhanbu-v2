<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ data: any }>()

// 紫微 12 宫顺序固定布局到 4x4 网格（去掉中间 4 格放命主信息）
// 标准布局：
//   巳 午 未 申
//   辰 [中心] 酉
//   卯 [中心] 戌
//   寅 丑 子 亥
const GRID_LAYOUT = [
  ['巳', '午', '未', '申'],
  ['辰', null, null, '酉'],
  ['卯', null, null, '戌'],
  ['寅', '丑', '子', '亥'],
]

const palaceMap = computed(() => {
  const m: Record<string, any> = {}
  for (const p of props.data?.palaces || []) m[p.zhi] = p
  return m
})
</script>

<template>
  <div v-if="data" class="glass p-5 md:p-6 space-y-4">
    <header class="flex items-center justify-between flex-wrap gap-2">
      <h3 class="title-zh flex items-center gap-2">
        <span class="seal text-sm">紫</span>紫微斗数
      </h3>
      <div class="text-xs text-ink-500 flex gap-3">
        <span>命宫 <span class="ganzhi text-base ml-1">{{ data.ming_gong?.ganzhi }}</span></span>
        <span>身宫 <span class="text-ember-300">{{ data.shen_gong?.zhi }}</span></span>
        <span>{{ data.wu_xing_ju?.name }}</span>
      </div>
    </header>

    <!-- 紫微宫位 4x4 网格 -->
    <div class="grid grid-cols-4 gap-1.5 aspect-square max-w-md mx-auto md:max-w-none">
      <template v-for="(row, ri) in GRID_LAYOUT" :key="ri">
        <template v-for="(zhi, ci) in row" :key="`${ri}-${ci}`">
          <!-- 边缘宫位 -->
          <div v-if="zhi"
               class="rounded-md bg-ink-900/40 border border-ink-600/50
                      p-1.5 text-[10px] md:text-xs
                      hover:border-ember-500/60 hover:bg-ink-900/70 transition
                      flex flex-col"
               :class="{
                 'border-ember-500/70 bg-ember-500/10': palaceMap[zhi]?.name === '命宫',
                 'ring-1 ring-gold-400/50': palaceMap[zhi]?.is_shen_gong,
               }">
            <div class="flex justify-between items-start mb-1">
              <span class="text-ember-300 font-kai">{{ palaceMap[zhi]?.name }}</span>
              <span class="text-[9px] text-ink-500">{{ palaceMap[zhi]?.ganzhi }}</span>
            </div>
            <div class="flex flex-wrap gap-0.5 flex-1 content-start">
              <span v-for="s in palaceMap[zhi]?.stars || []" :key="s.name"
                    class="text-[9px] md:text-[10px] px-1 rounded
                           bg-ink-700/60 text-slate-200">
                {{ s.name }}<span v-if="s.si_hua" class="text-ember-400">·{{ s.si_hua }}</span>
              </span>
            </div>
          </div>
          <!-- 中心区域 (合并显示命主信息) -->
          <div v-else-if="ri === 1 && ci === 1"
               class="row-span-2 col-span-2 rounded-md
                      bg-gradient-to-br from-ember-500/10 to-ink-900/40
                      border border-ember-500/30
                      flex flex-col items-center justify-center text-center p-3">
            <div class="font-kai text-lg md:text-xl text-ember-300 tracking-widest">命盘</div>
            <div class="text-[10px] text-ink-500 mt-1">{{ data.lunar?.year_ganzhi }}年</div>
            <div class="text-[10px] text-ink-500">{{ data.wu_xing_ju?.name }}</div>
            <div class="text-[10px] text-gold-400 mt-1">
              紫微 {{ data.ziwei_position }}
            </div>
            <div class="text-[9px] text-ink-500 mt-2 space-y-0.5">
              <div>禄 {{ data.si_hua?.['禄'] }}</div>
              <div>权 {{ data.si_hua?.['权'] }}</div>
              <div>科 {{ data.si_hua?.['科'] }}</div>
              <div>忌 {{ data.si_hua?.['忌'] }}</div>
            </div>
          </div>
        </template>
      </template>
    </div>

    <div class="text-[10px] text-ink-500 italic">{{ data.note }}</div>
  </div>
</template>
