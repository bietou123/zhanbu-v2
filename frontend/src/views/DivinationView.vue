<script setup lang="ts">
import { ref } from 'vue'
import AnalysisPanel from '@/components/AnalysisPanel.vue'
import { divinationAPI } from '@/api/client'

const mode = ref<'coin' | 'numbers'>('coin')
const numbers = ref({ n1: 1, n2: 1, n3: 1 })
const result = ref<any>(null)
const loading = ref(false)
const error = ref<string | null>(null)

async function cast() {
  loading.value = true; error.value = null
  try {
    if (mode.value === 'coin') {
      result.value = (await divinationAPI.coin()).data
    } else {
      result.value = (await divinationAPI.numbers(numbers.value.n1, numbers.value.n2, numbers.value.n3)).data
    }
  } catch (e: any) { error.value = e?.response?.data?.detail || e?.message }
  finally { loading.value = false }
}

function yaoLine(v: number, moving: boolean) {
  if (v === 1) {
    return moving ? '━━━━━ ⊙' : '━━━━━'
  }
  return moving ? '━━  ━━ ⊙' : '━━  ━━'
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="font-kai text-3xl md:text-4xl text-ember-400 tracking-widest">占卜起卦</h1>
      <p class="text-sm text-ink-500 mt-1">六爻金钱卦 · 本/变/互/错/综 五卦同呈</p>
    </div>

    <div class="glass p-5 md:p-6 space-y-4">
      <div class="flex gap-2">
        <button @click="mode = 'coin'" class="flex-1 px-5 py-2 rounded-xl border transition"
                :class="mode === 'coin' ? 'bg-ember-500/20 border-ember-500 text-ember-300' : 'btn-ghost'">
          摇钱起卦
        </button>
        <button @click="mode = 'numbers'" class="flex-1 px-5 py-2 rounded-xl border transition"
                :class="mode === 'numbers' ? 'bg-ember-500/20 border-ember-500 text-ember-300' : 'btn-ghost'">
          三数起卦
        </button>
      </div>

      <div v-if="mode === 'numbers'" class="grid grid-cols-3 gap-3">
        <label><span class="text-xs text-ink-500">上卦数</span>
          <input v-model.number="numbers.n1" type="number" min="1" class="input-base"/>
        </label>
        <label><span class="text-xs text-ink-500">下卦数</span>
          <input v-model.number="numbers.n2" type="number" min="1" class="input-base"/>
        </label>
        <label><span class="text-xs text-ink-500">动爻数</span>
          <input v-model.number="numbers.n3" type="number" min="1" class="input-base"/>
        </label>
      </div>

      <button @click="cast" :disabled="loading" class="btn-primary w-full md:w-auto">
        <span class="font-kai mr-1">摇</span>{{ loading ? '起卦中…' : '起卦' }}
      </button>
    </div>

    <div v-if="error" class="glass p-6 border-red-500/40 text-red-300 text-sm">✗ {{ error }}</div>

    <template v-if="result">
      <!-- 本卦 & 变卦 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="(g, label) in { 本卦: result.ben_gua, 变卦: result.bian_gua }" :key="label"
             class="glass p-5 space-y-3">
          <div class="flex justify-between items-baseline">
            <h3 class="title-zh">{{ label }}</h3>
            <span class="font-kai text-2xl text-ember-400">{{ g.name }}</span>
          </div>
          <!-- 6 爻自上而下 -->
          <div class="font-mono text-center space-y-1 leading-tight">
            <div v-for="i in [5,4,3,2,1,0]" :key="i"
                 class="text-xl tracking-widest"
                 :class="result.moving_yao_indexes_bottom_up?.includes(i) && label === '本卦'
                   ? 'text-ember-400' : g.yao_bottom_up[i] === 1 ? 'text-gold-400' : 'text-slate-400'">
              {{ yaoLine(g.yao_bottom_up[i], result.moving_yao_indexes_bottom_up?.includes(i) && label === '本卦') }}
            </div>
          </div>
          <div class="text-xs text-ink-500 text-center">
            上卦 {{ g.upper }} · 下卦 {{ g.lower }}
          </div>
          <div class="text-xs text-slate-300 leading-relaxed pt-2 border-t border-ink-600/40">
            {{ g.judgement }}
          </div>
        </div>
      </div>

      <!-- 互/错/综 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div v-for="(g, label) in { 互卦: result.hu_gua, 错卦: result.cuo_gua, 综卦: result.zong_gua }" :key="label"
             class="glass p-4">
          <div class="flex justify-between items-baseline mb-2">
            <span class="text-xs text-ink-500">{{ label }}</span>
            <span class="font-kai text-lg text-gold-400">{{ g.name }}</span>
          </div>
          <div class="text-xs text-slate-400">{{ g.judgement }}</div>
        </div>
      </div>

      <AnalysisPanel v-if="result.analysis" title="占卜解读"
                     :analysis="result.analysis" accent="ember" />
    </template>

    <div v-else-if="!error" class="glass p-12 text-center">
      <div class="text-6xl mb-4 opacity-30 font-kai animate-float">⚊</div>
      <p class="text-slate-400">心诚则灵，按钮起卦</p>
    </div>
  </div>
</template>
