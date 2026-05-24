<script setup lang="ts">
import { ref } from 'vue'
import BirthInputForm from '@/components/BirthInputForm.vue'
import BaziPlate from '@/components/BaziPlate.vue'
import ZiweiPlate from '@/components/ZiweiPlate.vue'
import QimenPlate from '@/components/QimenPlate.vue'
import { dashboardAPI, type BirthInput } from '@/api/client'

const loading = ref(false)
const error = ref<string | null>(null)
const triple = ref<any>(null)

// 移动端切换：bazi/ziwei/qimen
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
    <!-- 顶部标题 -->
    <div class="flex items-center justify-between flex-wrap gap-3">
      <div>
        <h1 class="font-kai text-3xl md:text-4xl text-ember-400 tracking-widest">三盘工作台</h1>
        <p class="text-sm text-ink-500 mt-1">八字 · 紫微 · 奇门，同屏联动</p>
      </div>
      <span class="text-xs text-ink-500 hidden md:block">
        历法核心：真太阳时校准 · lunar-python · PyEphem
      </span>
    </div>

    <!-- 输入表单 -->
    <BirthInputForm @submit="onSubmit" />

    <!-- 加载/错误状态 -->
    <div v-if="loading" class="glass p-12 text-center text-ember-300 animate-pulse">
      <span class="font-kai text-2xl">起盘中</span>
    </div>
    <div v-else-if="error" class="glass p-6 border-red-500/40 text-red-300 text-sm">
      ✗ {{ error }}
    </div>

    <!-- 三盘联动展示 -->
    <template v-else-if="triple">
      <!-- 真太阳时与历法信息条 -->
      <div class="glass px-4 py-2 text-[10px] md:text-xs text-ink-500 font-mono overflow-x-auto whitespace-nowrap">
        {{ ctxLine(triple) }}
      </div>

      <!-- 桌面端：三栏分屏 -->
      <div class="hidden lg:grid lg:grid-cols-3 gap-4 xl:gap-6">
        <BaziPlate :data="triple.bazi" />
        <ZiweiPlate :data="triple.ziwei" />
        <QimenPlate :data="triple.qimen" />
      </div>

      <!-- 平板端：两栏 + 八字独占一行 -->
      <div class="hidden md:grid md:grid-cols-2 lg:hidden gap-4">
        <BaziPlate :data="triple.bazi" class="md:col-span-2" />
        <ZiweiPlate :data="triple.ziwei" />
        <QimenPlate :data="triple.qimen" />
      </div>

      <!-- 手机端：tab 切换 -->
      <div class="md:hidden space-y-4">
        <div class="flex gap-1 glass p-1">
          <button v-for="t in [{k:'bazi',n:'八字'},{k:'ziwei',n:'紫微'},{k:'qimen',n:'奇门'}]"
                  :key="t.k"
                  @click="mobileTab = t.k as any"
                  class="flex-1 py-2 rounded-lg text-sm transition"
                  :class="mobileTab === t.k
                    ? 'bg-ember-500/30 text-white shadow-glow-ember'
                    : 'text-slate-400'">
            {{ t.n }}
          </button>
        </div>
        <BaziPlate v-if="mobileTab === 'bazi'" :data="triple.bazi" />
        <ZiweiPlate v-if="mobileTab === 'ziwei'" :data="triple.ziwei" />
        <QimenPlate v-if="mobileTab === 'qimen'" :data="triple.qimen" />
      </div>
    </template>

    <!-- 空状态 -->
    <div v-else class="glass p-12 text-center">
      <div class="text-6xl mb-4 opacity-30 font-kai animate-float">☯</div>
      <p class="text-slate-400">输入生辰信息，开始三盘联动排盘</p>
    </div>
  </div>
</template>
