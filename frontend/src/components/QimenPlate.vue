<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ data: any }>()

// 九宫格按洛书布局：
//  4(巽东南) 9(离南)  2(坤西南)
//  3(震东)   5(中)    7(兑西)
//  8(艮东北) 1(坎北)  6(乾西北)
const LO_SHU = [
  [4, 9, 2],
  [3, 5, 7],
  [8, 1, 6],
]

const palaceMap = computed(() => {
  const m: Record<number, any> = {}
  for (const p of props.data?.palaces || []) m[p.palace] = p
  return m
})
</script>

<template>
  <div v-if="data" class="glass p-5 md:p-6 space-y-4">
    <header class="flex items-center justify-between flex-wrap gap-2">
      <h3 class="title-zh flex items-center gap-2">
        <span class="seal text-sm">奇</span>奇门遁甲
      </h3>
      <div class="text-xs text-ink-500 flex gap-3 flex-wrap">
        <span>{{ data.jieqi }}</span>
        <span class="text-ember-300">{{ data.ju_label }}</span>
        <span>{{ data.yuan }}</span>
        <span>日 {{ data.day_ganzhi }}</span>
        <span>时 {{ data.hour_ganzhi }}</span>
      </div>
    </header>

    <!-- 9 宫 -->
    <div class="grid grid-cols-3 gap-1.5 aspect-square max-w-md mx-auto md:max-w-none">
      <template v-for="row in LO_SHU">
        <div v-for="num in row" :key="num"
             class="rounded-md p-2 md:p-3 text-[10px] md:text-xs
                    bg-ink-900/40 border border-ink-600/50
                    hover:border-ember-500/50 transition
                    flex flex-col"
             :class="{
               'border-ember-500/60 bg-ember-500/10':
                 num === data.zhi_fu_zhi_shi?.zhi_fu_palace,
               'ring-1 ring-gold-400/50':
                 num === data.zhi_fu_zhi_shi?.zhi_shi_palace,
             }">
          <div class="flex justify-between items-center mb-1">
            <span class="text-ember-300 font-kai">{{ palaceMap[num]?.bagua }}</span>
            <span class="text-[9px] text-ink-500">{{ num }}宫</span>
          </div>
          <div class="space-y-1 flex-1">
            <div class="ganzhi text-xl md:text-2xl text-center">{{ palaceMap[num]?.di_pan }}</div>
            <div class="flex justify-between text-[9px] text-slate-400">
              <span>{{ palaceMap[num]?.star }}</span>
              <span class="text-ember-300">{{ palaceMap[num]?.gate || '—' }}</span>
            </div>
          </div>
          <div class="text-[8px] text-ink-500 text-center mt-1">{{ palaceMap[num]?.direction }}</div>
        </div>
      </template>
    </div>

    <div class="text-xs grid grid-cols-2 gap-2">
      <div class="rounded-md bg-ink-900/40 border border-ember-500/40 p-2">
        值符 · <span class="text-ember-300">{{ data.zhi_fu_zhi_shi?.zhi_fu_star }}</span>
        <span class="text-ink-500 ml-1">{{ data.zhi_fu_zhi_shi?.zhi_fu_palace }}宫</span>
      </div>
      <div class="rounded-md bg-ink-900/40 border border-gold-400/40 p-2">
        值使 · <span class="text-gold-400">{{ data.zhi_fu_zhi_shi?.zhi_shi_gate }}</span>
        <span class="text-ink-500 ml-1">{{ data.zhi_fu_zhi_shi?.zhi_shi_palace }}宫</span>
      </div>
    </div>

    <div class="text-[10px] text-ink-500 italic">{{ data.note }}</div>
  </div>
</template>
