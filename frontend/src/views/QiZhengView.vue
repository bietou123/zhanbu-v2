<script setup lang="ts">
import { ref, computed } from 'vue'
import BirthInputForm from '@/components/BirthInputForm.vue'
import { qizhengAPI, type BirthInput } from '@/api/client'

const loading = ref(false)
const error = ref<string | null>(null)
const data = ref<any>(null)

async function onSubmit(p: BirthInput) {
  loading.value = true; error.value = null
  try { data.value = (await qizhengAPI.compute(p)).data }
  catch (e: any) { error.value = e?.response?.data?.detail || e?.message }
  finally { loading.value = false }
}

const allBodies = computed(() => {
  if (!data.value) return []
  const out: any[] = []
  for (const [k, v] of Object.entries(data.value.seven_zheng || {})) {
    out.push({ name: k, type: '七政', ...(v as any) })
  }
  for (const [k, v] of Object.entries(data.value.four_yu || {})) {
    out.push({ name: k, type: '四余', ...(v as any) })
  }
  return out
})

// 星盘圆形 SVG（黄道 12 宫）
const RADIUS = 220
const CENTER = 240
const ZODIAC = ['白羊','金牛','双子','巨蟹','狮子','处女','天秤','天蝎','射手','摩羯','水瓶','双鱼']

function polarToXY(longitudeDeg: number, r: number) {
  // 占星界惯例：白羊 0° 在 9 点钟方向（左），逆时针
  const rad = ((180 - longitudeDeg) * Math.PI) / 180
  return { x: CENTER + r * Math.cos(rad), y: CENTER - r * Math.sin(rad) }
}

function bodySymbol(name: string) {
  return ({
    太阳: '☉', 太阴: '☽', 水星: '☿', 金星: '♀', 火星: '♂', 木星: '♃', 土星: '♄',
    罗睺: '☊', 计都: '☋', 月孛: '⚸', 紫炁: '✦',
  } as Record<string, string>)[name] || '·'
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="font-kai text-3xl md:text-4xl text-ember-400 tracking-widest">七政四余</h1>
      <p class="text-sm text-ink-500 mt-1">古典星命学 · 行星黄经 + 月交点 + 月孛 + 紫炁</p>
    </div>

    <BirthInputForm @submit="onSubmit" />

    <div v-if="loading" class="glass p-12 text-center text-ember-300 animate-pulse">
      <span class="font-kai text-2xl">推算行星位置中</span>
    </div>
    <div v-else-if="error" class="glass p-6 border-red-500/40 text-red-300 text-sm">✗ {{ error }}</div>

    <template v-else-if="data">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6">
        <!-- 星盘可视化 -->
        <div class="glass p-4 lg:col-span-2 overflow-hidden">
          <h3 class="title-zh flex items-center gap-2 mb-3">
            <span class="seal text-sm">天</span>黄道盘
          </h3>
          <svg :viewBox="`0 0 ${CENTER*2} ${CENTER*2}`" class="w-full max-w-[480px] mx-auto">
            <!-- 外圈 -->
            <circle :cx="CENTER" :cy="CENTER" :r="RADIUS" fill="none" stroke="rgba(212,176,97,0.4)" stroke-width="2"/>
            <circle :cx="CENTER" :cy="CENTER" :r="RADIUS-40" fill="none" stroke="rgba(212,176,97,0.18)" stroke-width="1"/>
            <!-- 12 宫分隔线 + 名字 -->
            <g v-for="(z, i) in ZODIAC" :key="z">
              <line :x1="polarToXY(i*30, RADIUS-40).x" :y1="polarToXY(i*30, RADIUS-40).y"
                    :x2="polarToXY(i*30, RADIUS).x" :y2="polarToXY(i*30, RADIUS).y"
                    stroke="rgba(212,176,97,0.3)" stroke-width="1"/>
              <text :x="polarToXY(i*30+15, RADIUS-20).x" :y="polarToXY(i*30+15, RADIUS-20).y"
                    text-anchor="middle" dominant-baseline="middle"
                    fill="#d4b061" font-size="13" font-family="KaiTi, serif">
                {{ z }}
              </text>
            </g>
            <!-- 中心 -->
            <text :x="CENTER" :y="CENTER-10" text-anchor="middle" fill="#e07b3c"
                  font-family="KaiTi, serif" font-size="22" font-weight="bold">命盘</text>
            <text :x="CENTER" :y="CENTER+18" text-anchor="middle" fill="#7dd3a8" font-size="10">
              JD {{ data.julian_day_ut?.toFixed(2) }}
            </text>
            <!-- 行星 -->
            <g v-for="b in allBodies" :key="b.name">
              <circle :cx="polarToXY(b.longitude, RADIUS-90).x"
                      :cy="polarToXY(b.longitude, RADIUS-90).y"
                      r="14" fill="rgba(26,31,44,0.95)"
                      :stroke="b.type === '七政' ? '#e07b3c' : '#7dd3a8'"
                      stroke-width="1.5"/>
              <text :x="polarToXY(b.longitude, RADIUS-90).x"
                    :y="polarToXY(b.longitude, RADIUS-90).y+5"
                    text-anchor="middle" fill="#fff" font-size="16">{{ bodySymbol(b.name) }}</text>
              <text :x="polarToXY(b.longitude, RADIUS-115).x"
                    :y="polarToXY(b.longitude, RADIUS-115).y+3"
                    text-anchor="middle" fill="#d4b061" font-size="9">{{ b.name }}</text>
            </g>
          </svg>
        </div>

        <!-- 表格 -->
        <div class="glass p-4 overflow-auto">
          <h3 class="title-zh mb-3 flex items-center gap-2">
            <span class="seal text-sm">星</span>星体一览
          </h3>
          <table class="w-full text-xs">
            <thead class="text-ink-500 border-b border-ink-600/60">
              <tr><th class="text-left py-2">星</th><th class="text-left">类</th>
                  <th class="text-left">宫</th><th class="text-left">度</th><th class="text-left">宿</th></tr>
            </thead>
            <tbody>
              <tr v-for="b in allBodies" :key="b.name"
                  class="border-b border-ink-600/30 hover:bg-ink-900/40 transition">
                <td class="py-1.5">
                  <span class="mr-1" :class="b.type === '七政' ? 'text-ember-300' : 'text-jade-400'">
                    {{ bodySymbol(b.name) }}
                  </span>
                  {{ b.name }}
                </td>
                <td class="text-ink-500">{{ b.type }}</td>
                <td>{{ b.zodiac }}</td>
                <td class="font-mono">{{ b.degree?.toFixed(1) }}°</td>
                <td class="text-gold-400">{{ b.xiu }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="text-[10px] text-ink-500 italic">{{ data.note }}</div>
    </template>

    <div v-else class="glass p-12 text-center">
      <div class="text-6xl mb-4 opacity-30 font-kai animate-float">★</div>
      <p class="text-slate-400">输入生辰，绘制古典星盘</p>
    </div>
  </div>
</template>
