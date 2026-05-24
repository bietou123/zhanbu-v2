<script setup lang="ts">
import { ref } from 'vue'
import BirthInputForm from '@/components/BirthInputForm.vue'
import AnalysisPanel from '@/components/AnalysisPanel.vue'
import { meihuaAPI, type BirthInput } from '@/api/client'

type Mode = 'time' | 'chars' | 'numbers'
const mode = ref<Mode>('time')
const chars = ref({ part1: '', part2: '' })
const numbers = ref({ n1: 3, n2: 5 })
const loading = ref(false)
const error = ref<string | null>(null)
const result = ref<any>(null)

async function castByTime(p: BirthInput) {
  loading.value = true; error.value = null
  try { result.value = (await meihuaAPI.byTime(p)).data }
  catch (e: any) { error.value = e?.response?.data?.detail || e?.message }
  finally { loading.value = false }
}

async function castByChars() {
  loading.value = true; error.value = null
  try { result.value = (await meihuaAPI.byChars(chars.value.part1, chars.value.part2)).data }
  catch (e: any) { error.value = e?.response?.data?.detail || e?.message }
  finally { loading.value = false }
}

async function castByNumbers() {
  loading.value = true; error.value = null
  try { result.value = (await meihuaAPI.byNumbers(numbers.value.n1, numbers.value.n2)).data }
  catch (e: any) { error.value = e?.response?.data?.detail || e?.message }
  finally { loading.value = false }
}

const relationColor = (rel: string) => {
  if (!rel) return 'text-slate-400'
  if (rel.includes('大吉')) return 'text-jade-400'
  if (rel.includes('凶')) return 'text-red-400'
  if (rel.includes('比和')) return 'text-amber-300'
  return 'text-ember-300'
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="font-kai text-3xl md:text-4xl text-ember-400 tracking-widest">梅花易数</h1>
      <p class="text-sm text-ink-500 mt-1">邵雍心易 · 体用生克</p>
    </div>

    <div class="flex gap-2">
      <button v-for="m in [{k:'time',n:'时间起卦'},{k:'chars',n:'字数起卦'},{k:'numbers',n:'二数起卦'}]"
              :key="m.k" @click="mode = m.k as Mode; result = null"
              class="flex-1 md:flex-none px-5 py-2 rounded-xl border transition"
              :class="mode === m.k ? 'bg-ember-500/20 border-ember-500 text-ember-300' : 'btn-ghost'">
        {{ m.n }}
      </button>
    </div>

    <BirthInputForm v-if="mode === 'time'" @submit="castByTime" />

    <div v-if="mode === 'chars'" class="glass p-5 space-y-3">
      <label><span class="text-xs text-ink-500">第一段文字 (上卦)</span>
        <input v-model="chars.part1" class="input-base" placeholder="如：花开"/>
      </label>
      <label><span class="text-xs text-ink-500">第二段文字 (下卦)</span>
        <input v-model="chars.part2" class="input-base" placeholder="如：富贵临门"/>
      </label>
      <button @click="castByChars" :disabled="loading" class="btn-primary">起卦</button>
    </div>

    <div v-if="mode === 'numbers'" class="glass p-5 space-y-3">
      <div class="grid grid-cols-2 gap-3">
        <label><span class="text-xs text-ink-500">数 1 (上卦)</span>
          <input v-model.number="numbers.n1" type="number" min="1" class="input-base"/>
        </label>
        <label><span class="text-xs text-ink-500">数 2 (下卦)</span>
          <input v-model.number="numbers.n2" type="number" min="1" class="input-base"/>
        </label>
      </div>
      <button @click="castByNumbers" :disabled="loading" class="btn-primary">起卦</button>
    </div>

    <div v-if="error" class="glass p-6 border-red-500/40 text-red-300 text-sm">✗ {{ error }}</div>

    <template v-if="result">
      <!-- 体用关系卡（核心） -->
      <div class="glass p-5 md:p-6 border-2"
           :class="result.ti_yong?.relation.includes('凶') ? 'border-red-500/40' :
                   result.ti_yong?.relation.includes('吉') ? 'border-jade-500/40' :
                   'border-ember-500/40'">
        <div class="text-xs text-ink-500 mb-3">体用判定</div>
        <div class="flex items-center justify-around">
          <div class="text-center">
            <div class="text-xs text-ink-500">体卦</div>
            <div class="font-kai text-4xl text-ember-300">{{ result.ti_yong?.ti.gua }}</div>
            <div class="text-xs text-gold-400 mt-1">{{ result.ti_yong?.ti.wuxing }}</div>
          </div>
          <div class="text-2xl font-kai" :class="relationColor(result.ti_yong?.relation)">
            ⇄
          </div>
          <div class="text-center">
            <div class="text-xs text-ink-500">用卦</div>
            <div class="font-kai text-4xl text-jade-400">{{ result.ti_yong?.yong.gua }}</div>
            <div class="text-xs text-gold-400 mt-1">{{ result.ti_yong?.yong.wuxing }}</div>
          </div>
        </div>
        <div class="text-center mt-4 font-kai text-xl"
             :class="relationColor(result.ti_yong?.relation)">
          {{ result.ti_yong?.relation }}
        </div>
      </div>

      <!-- 本/互/变 三卦 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="(g, label) in { 本卦: result.ben_gua, 互卦: result.hu_gua, 变卦: result.bian_gua }"
             :key="label"
             class="glass p-4">
          <div class="flex justify-between items-baseline mb-2">
            <span class="text-xs text-ink-500">{{ label }}</span>
            <span class="font-kai text-xl text-ember-400">{{ g.name }}</span>
          </div>
          <div class="text-[10px] text-ink-500">{{ g.upper }} / {{ g.lower }}</div>
          <div class="text-xs text-slate-300 mt-2 leading-relaxed">{{ g.judgement }}</div>
        </div>
      </div>

      <AnalysisPanel v-if="result.analysis" title="梅花解读"
                     :analysis="result.analysis" accent="cyber" />
    </template>

    <div v-else-if="!error && mode !== 'time'" class="glass p-12 text-center">
      <div class="text-6xl mb-4 opacity-30 font-kai animate-float">梅</div>
      <p class="text-slate-400">心动起卦</p>
    </div>
  </div>
</template>
