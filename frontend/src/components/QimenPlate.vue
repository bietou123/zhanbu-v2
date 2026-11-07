<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{ data: any; patterns?: any }>()

// 洛书九宫
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

// 格局判定结果：{patterns, ji, xiong, score_delta, summary}
const patternList = computed<any[]>(() => props.patterns?.patterns || [])
const patternScore = computed<number>(() => props.patterns?.score_delta ?? 0)

const luckColor = (l: string) => ({
  '大吉': 'text-jade-400',
  '吉': 'text-jade-400',
  '小吉': 'text-amber-300',
  '中': 'text-slate-300',
  '中平': 'text-slate-300',
  '小凶': 'text-orange-400',
  '凶': 'text-red-400',
  '大凶': 'text-red-500',
}[l] || 'text-slate-400')
</script>

<template>
  <div v-if="data" class="glass glass-neon p-5 md:p-6 space-y-4">
    <header class="flex items-center justify-between flex-wrap gap-2">
      <h3 class="title-zh flex items-center gap-2">
        <span class="seal text-sm">奇</span>奇门遁甲
      </h3>
      <div class="text-[10px] text-ink-500 flex gap-2 flex-wrap font-mono">
        <span class="chip">{{ data.jieqi }}</span>
        <span class="chip-ember">{{ data.ju_label }}</span>
        <span class="chip">{{ data.yuan }}</span>
        <span class="chip-mystic">日 {{ data.day_ganzhi }}</span>
        <span class="chip-mystic">时 {{ data.hour_ganzhi }}</span>
      </div>
    </header>

    <!-- 9 宫 -->
    <div class="grid grid-cols-3 gap-1.5 aspect-square max-w-md mx-auto md:max-w-none">
      <template v-for="row in LO_SHU">
        <div v-for="num in row" :key="num"
             class="rounded-md p-1.5 md:p-2 text-[9px] md:text-[10px]
                    bg-ink-900/50 border border-ink-600/50
                    hover:border-cyber-400/60 transition
                    flex flex-col relative overflow-hidden"
             :class="{
               'border-ember-500/60 bg-ember-500/10 shadow-glow-ember':
                 palaceMap[num]?.is_zhi_fu_palace,
               'ring-1 ring-cyber-400/60':
                 palaceMap[num]?.is_zhi_shi_palace,
             }">
          <!-- 顶部：八卦 + 宫号 -->
          <div class="flex justify-between items-center mb-1">
            <span class="font-kai text-ember-300">{{ palaceMap[num]?.bagua }}</span>
            <span class="text-[8px] text-ink-500">{{ num }}宫</span>
          </div>

          <!-- 中部：八神 -->
          <div class="text-center text-[9px] mb-0.5">
            <span class="chip-mystic !py-0">{{ palaceMap[num]?.spirit || '—' }}</span>
          </div>

          <!-- 主体：天盘/地盘 双干 -->
          <div class="flex items-center justify-center gap-1 my-0.5">
            <span class="font-kai text-base md:text-lg text-cyber-300">{{ palaceMap[num]?.tian_pan_gan }}</span>
            <span class="text-ink-500 text-[8px]">/</span>
            <span class="font-kai text-base md:text-lg text-gold-400">{{ palaceMap[num]?.di_pan_gan }}</span>
          </div>

          <!-- 星 / 门 -->
          <div class="space-y-0.5 mt-auto">
            <div class="flex justify-between" :class="luckColor(palaceMap[num]?.star_luck)">
              <span>{{ palaceMap[num]?.star }}</span>
              <span class="text-[8px] opacity-70">{{ palaceMap[num]?.star_luck }}</span>
            </div>
            <div class="flex justify-between"
                 :class="luckColor(palaceMap[num]?.gate_luck)">
              <span>{{ palaceMap[num]?.gate || '—' }}</span>
              <span class="text-[8px] opacity-70">{{ palaceMap[num]?.gate_luck || '' }}</span>
            </div>
          </div>

          <!-- 方位 -->
          <div class="text-[8px] text-ink-500 text-center mt-1">
            {{ palaceMap[num]?.direction }}
          </div>
        </div>
      </template>
    </div>

    <!-- 值符/值使 -->
    <div class="grid grid-cols-2 gap-2 text-xs">
      <div class="rounded-md bg-ink-900/40 border border-ember-500/40 p-2">
        <div class="text-[10px] text-ink-500 mb-0.5">值符</div>
        <div class="font-kai text-ember-300">{{ data.zhi_fu_zhi_shi?.zhi_fu_star }}</div>
        <div class="text-[10px] text-slate-400">
          原 {{ data.zhi_fu_zhi_shi?.zhi_fu_orig_palace }}宫 → 飞 {{ data.zhi_fu_zhi_shi?.zhi_fu_now_palace }}宫
        </div>
      </div>
      <div class="rounded-md bg-ink-900/40 border border-cyber-400/40 p-2">
        <div class="text-[10px] text-ink-500 mb-0.5">值使</div>
        <div class="font-kai text-cyber-300">{{ data.zhi_fu_zhi_shi?.zhi_shi_gate }}</div>
        <div class="text-[10px] text-slate-400">
          原 {{ data.zhi_fu_zhi_shi?.zhi_shi_orig_palace }}宫 → 飞 {{ data.zhi_fu_zhi_shi?.zhi_shi_now_palace }}宫
        </div>
      </div>
    </div>

    <!-- 格局判定 -->
    <div v-if="patterns" class="rounded-md bg-ink-900/40 border border-ink-600/40 p-3 space-y-2">
      <div class="flex items-center justify-between">
        <div class="text-[10px] text-ink-500">格局</div>
        <div class="text-[10px] font-mono"
             :class="patternScore > 0 ? 'text-jade-400'
                   : patternScore < 0 ? 'text-red-300' : 'text-slate-400'">
          {{ patternScore > 0 ? '+' : '' }}{{ patternScore }}
        </div>
      </div>

      <div v-if="patternList.length" class="space-y-1">
        <div v-for="(p, i) in patternList" :key="i" class="flex items-start gap-1.5">
          <span class="text-[9px] md:text-[10px] px-1 rounded shrink-0"
                :class="p.type === '吉'
                  ? 'bg-jade-500/10 text-jade-400 border border-jade-500/40'
                  : 'bg-red-500/10 text-red-300 border border-red-500/40'">
            {{ p.name }}
          </span>
          <span class="text-[9px] md:text-[10px] text-slate-400 leading-relaxed">
            {{ p.detail }}
          </span>
        </div>
      </div>
      <div v-else class="text-[10px] text-ink-500 italic">
        本盘未见常见吉凶格局，以值符值使与用神宫位为主判断。
      </div>
    </div>

    <div class="text-[10px] text-ink-500 italic">{{ data.note }}</div>
  </div>
</template>
