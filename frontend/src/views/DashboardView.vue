<script setup lang="ts">
import { ref } from 'vue'
import BirthInputForm from '@/components/BirthInputForm.vue'
import BaziPlate from '@/components/BaziPlate.vue'
import ZiweiPlate from '@/components/ZiweiPlate.vue'
import QimenPlate from '@/components/QimenPlate.vue'
import AnalysisPanel from '@/components/AnalysisPanel.vue'
import { dashboardAPI, type BirthInput } from '@/api/client'

const loading = ref(false)
const error = ref<string | null>(null)
const triple = ref<any>(null)
const mobileTab = ref<'bazi' | 'ziwei' | 'qimen'>('bazi')

async function onSubmit(p: BirthInput) {
  loading.value = true
  error.value = null
  try {
    const resp = await dashboardAPI.triple(p)
    triple.value = resp.data
  } catch (e: any) {
    error.value = e?.response?.data?.detail || e?.message || '请求失败'
  } finally {
    loading.value = false
  }
}

const ctxLine = (d: any) => {
  if (!d?.bazi?.context) return ''
  const ctx = d.bazi.context
  return `公历 ${ctx.solar_civil} · 真太阳时 ${ctx.true_solar_time.true_solar_time}` +
    ` · 经度修正 ${ctx.true_solar_time.longitude_offset_min}min · 均时差 ${ctx.true_solar_time.eot_min}min`
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="font-kai text-3xl md:text-4xl tracking-widest"
            style="background: linear-gradient(90deg,#22d3ee,#e07b3c,#d4b061); -webkit-background-clip:text; background-clip:text; color:transparent;">
          三盘工作台
        </h1>
        <p class="text-sm text-ink-500 mt-1">
          <span class="title-cyber">DASHBOARD · TRIPLE PLATE</span>
        </p>
      </div>
      <span class="text-xs text-cyber-300/70 hidden md:block font-mono">
        真太阳时校准 · lunar-python · PyEphem
      </span>
    </div>

    <BirthInputForm @submit="onSubmit" />

    <div v-if="loading" class="glass glass-neon p-12 text-center">
      <div class="font-kai text-2xl text-cyber-300 animate-glow-pulse">起 盘 中</div>
      <div class="mt-3 text-xs font-mono text-cyber-400 tracking-widest">COMPUTING...</div>
    </div>
    <div v-else-if="error" class="glass p-6 border-red-500/40 text-red-300 text-sm">
      ✗ {{ error }}
    </div>

    <template v-else-if="triple">
      <div class="glass px-4 py-2 text-[10px] md:text-xs text-cyber-300/80 font-mono overflow-x-auto whitespace-nowrap">
        {{ ctxLine(triple) }}
      </div>

      <!-- 桌面端：三栏分屏 -->
      <div class="hidden lg:grid lg:grid-cols-3 gap-4 xl:gap-6">
        <BaziPlate :data="triple.bazi" />
        <ZiweiPlate :data="triple.ziwei" />
        <QimenPlate :data="triple.qimen" />
      </div>

      <!-- 平板端 -->
      <div class="hidden md:grid md:grid-cols-2 lg:hidden gap-4">
        <BaziPlate :data="triple.bazi" class="md:col-span-2" />
        <ZiweiPlate :data="triple.ziwei" />
        <QimenPlate :data="triple.qimen" />
      </div>

      <!-- 手机端 tab -->
      <div class="md:hidden space-y-4">
        <div class="flex gap-1 glass p-1">
          <button v-for="t in [{k:'bazi',n:'八字'},{k:'ziwei',n:'紫微'},{k:'qimen',n:'奇门'}]"
                  :key="t.k"
                  @click="mobileTab = t.k as any"
                  class="flex-1 py-2 rounded-lg text-sm transition"
                  :class="mobileTab === t.k
                    ? 'bg-cyber-500/30 text-white shadow-glow-cyber'
                    : 'text-slate-400'">
            {{ t.n }}
          </button>
        </div>
        <BaziPlate v-if="mobileTab === 'bazi'" :data="triple.bazi" />
        <ZiweiPlate v-if="mobileTab === 'ziwei'" :data="triple.ziwei" />
        <QimenPlate v-if="mobileTab === 'qimen'" :data="triple.qimen" />
      </div>

      <!-- 分析层：三盘各自的解读 -->
      <section class="space-y-4 pt-2">
        <h2 class="title-cyber flex items-center gap-2">
          <span class="seal-cyber text-xs">析</span>
          ANALYSIS · 综合解读
        </h2>
        <AnalysisPanel v-if="triple.bazi?.analysis" title="八字解读"
                       :analysis="triple.bazi.analysis" accent="ember" />
        <AnalysisPanel v-if="triple.ziwei?.analysis" title="紫微解读"
                       :analysis="triple.ziwei.analysis" accent="mystic" />
        <AnalysisPanel v-if="triple.qimen?.analysis" title="奇门解读"
                       :analysis="triple.qimen.analysis" accent="cyber" />
      </section>
    </template>

    <div v-else class="glass glass-neon p-12 text-center">
      <div class="text-6xl mb-4 opacity-50 font-kai animate-float text-cyber-400">☯</div>
      <p class="text-slate-400">输入生辰信息，开始三盘联动排盘</p>
      <p class="text-xs text-cyber-300/60 mt-2 font-mono tracking-widest">AWAITING INPUT...</p>
    </div>
  </div>
</template>
