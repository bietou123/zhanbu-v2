<script setup lang="ts">
defineProps<{ data: any }>()

const pillarLabels = [
  { key: 'year',  zh: '年柱', sub: '祖辈 / 童年' },
  { key: 'month', zh: '月柱', sub: '父母 / 青年' },
  { key: 'day',   zh: '日柱', sub: '自身 / 配偶' },
  { key: 'hour',  zh: '时柱', sub: '子女 / 晚景' },
]

const wuxingColors: Record<string, string> = {
  '金': 'text-yellow-200 bg-yellow-500/10 border-yellow-500/30',
  '木': 'text-jade-400 bg-jade-500/10 border-jade-500/30',
  '水': 'text-blue-300 bg-blue-500/10 border-blue-500/30',
  '火': 'text-ember-300 bg-ember-500/15 border-ember-500/40',
  '土': 'text-amber-300 bg-amber-500/10 border-amber-500/30',
}

const ganWuxing: Record<string, string> = {
  '甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土',
  '庚':'金','辛':'金','壬':'水','癸':'水',
}
const zhiWuxing: Record<string, string> = {
  '寅':'木','卯':'木','巳':'火','午':'火','辰':'土','戌':'土',
  '丑':'土','未':'土','申':'金','酉':'金','亥':'水','子':'水',
}
</script>

<template>
  <div v-if="data" class="glass p-5 md:p-6 space-y-5">
    <header class="flex items-center justify-between">
      <h3 class="title-zh flex items-center gap-2">
        <span class="seal text-sm">八</span>八字四柱
      </h3>
      <div class="text-xs text-ink-500">
        日主 <span class="ganzhi text-base ml-1"
          :class="wuxingColors[data.day_master?.wuxing] || 'text-gold-400'">
          {{ data.day_master?.gan }}
        </span>
        <span class="ml-1">{{ data.day_master?.wuxing }} · {{ data.day_master?.yin_yang }}</span>
      </div>
    </header>

    <!-- 四柱网格：手机两列、桌面四列 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div v-for="p in pillarLabels" :key="p.key"
           class="rounded-xl bg-ink-900/40 border border-ink-600/60 p-3 text-center
                  hover:border-ember-500/40 transition">
        <div class="text-[10px] text-ink-500 mb-1">{{ p.zh }}</div>
        <div class="ganzhi text-2xl md:text-3xl tracking-wider flex justify-center gap-1">
          <span :class="wuxingColors[ganWuxing[data.pillars[p.key][0]]]"
                class="px-1 rounded">{{ data.pillars[p.key][0] }}</span>
          <span :class="wuxingColors[zhiWuxing[data.pillars[p.key][1]]]"
                class="px-1 rounded">{{ data.pillars[p.key][1] }}</span>
        </div>
        <div class="text-[10px] text-ember-300 mt-1">{{ data.ten_gods?.gan[p.key] }}</div>
        <div class="text-[10px] text-ink-500 mt-0.5">{{ data.na_yin?.[p.key] }}</div>
      </div>
    </div>

    <!-- 五行强弱 -->
    <div>
      <div class="text-xs text-ink-500 mb-2">五行分布</div>
      <div class="flex gap-1 h-6 rounded-lg overflow-hidden border border-ink-600/60">
        <div v-for="(v, k) in data.wuxing_count" :key="k"
             :style="{ flex: v }"
             class="flex items-center justify-center text-[10px] font-medium"
             :class="{
               '金': 'bg-yellow-500/40 text-yellow-100',
               '木': 'bg-jade-500/40 text-jade-100',
               '水': 'bg-blue-500/40 text-blue-100',
               '火': 'bg-ember-500/40 text-ember-100',
               '土': 'bg-amber-500/40 text-amber-100',
             }[k]"
             :title="`${k} ${v}`">
          {{ v ? k + v : '' }}
        </div>
      </div>
    </div>

    <!-- 大运 -->
    <div>
      <div class="text-xs text-ink-500 mb-2">大运 · 十步</div>
      <div class="grid grid-cols-5 md:grid-cols-10 gap-1.5">
        <div v-for="d in data.da_yun" :key="d.index"
             class="rounded-md bg-ink-900/40 border border-ink-600/60 p-1.5 text-center
                    hover:border-ember-500/40 transition">
          <div class="text-[9px] text-ink-500">{{ d.start_age }}岁</div>
          <div class="ganzhi text-sm">{{ d.ganzhi }}</div>
          <div class="text-[9px] text-ink-500">{{ d.start_year }}</div>
        </div>
      </div>
    </div>

    <!-- 神煞方位 -->
    <details class="text-xs">
      <summary class="cursor-pointer text-ink-500 hover:text-ember-300">神煞方位</summary>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
        <div class="px-3 py-2 rounded-md bg-ink-900/40 border border-ink-600/40">
          喜神 <span class="text-ember-300">{{ data.shensha?.day_position_xi }}</span>
        </div>
        <div class="px-3 py-2 rounded-md bg-ink-900/40 border border-ink-600/40">
          阳贵 <span class="text-ember-300">{{ data.shensha?.day_position_yang_gui }}</span>
        </div>
        <div class="px-3 py-2 rounded-md bg-ink-900/40 border border-ink-600/40">
          阴贵 <span class="text-ember-300">{{ data.shensha?.day_position_yin_gui }}</span>
        </div>
        <div class="px-3 py-2 rounded-md bg-ink-900/40 border border-ink-600/40">
          福神 <span class="text-ember-300">{{ data.shensha?.day_position_fu }}</span>
        </div>
        <div class="px-3 py-2 rounded-md bg-ink-900/40 border border-ink-600/40">
          财神 <span class="text-ember-300">{{ data.shensha?.day_position_cai }}</span>
        </div>
      </div>
    </details>
  </div>
</template>
