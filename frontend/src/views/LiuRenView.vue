<script setup lang="ts">
import { ref } from 'vue'
import BirthInputForm from '@/components/BirthInputForm.vue'
import AnalysisPanel from '@/components/AnalysisPanel.vue'
import { liurenAPI, type BirthInput } from '@/api/client'

type Mode = 'da' | 'xiao'
const mode = ref<Mode>('xiao')
const loading = ref(false)
const error = ref<string | null>(null)
const da = ref<any>(null)
const xiao = ref<any>(null)

async function onSubmit(p: BirthInput) {
  loading.value = true; error.value = null
  try {
    if (mode.value === 'da') da.value = (await liurenAPI.da(p)).data
    else xiao.value = (await liurenAPI.xiao(p)).data
  } catch (e: any) { error.value = e?.response?.data?.detail || e?.message }
  finally { loading.value = false }
}

const guaColor: Record<string, string> = {
  '大安': 'bg-jade-500/20 border-jade-500/50 text-jade-400',
  '留连': 'bg-blue-500/20 border-blue-500/50 text-blue-300',
  '速喜': 'bg-ember-500/20 border-ember-500/50 text-ember-300',
  '赤口': 'bg-red-500/20 border-red-500/50 text-red-300',
  '小吉': 'bg-amber-500/20 border-amber-500/50 text-amber-300',
  '空亡': 'bg-ink-700/40 border-ink-500 text-ink-500',
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="font-kai text-3xl md:text-4xl text-ember-400 tracking-widest">六壬课</h1>
      <p class="text-sm text-ink-500 mt-1">小六壬（马前课）· 大六壬（四课三传）</p>
    </div>

    <div class="flex gap-2">
      <button @click="mode = 'xiao'" class="flex-1 md:flex-none px-5 py-2 rounded-xl border transition"
              :class="mode === 'xiao' ? 'bg-ember-500/20 border-ember-500 text-ember-300' : 'btn-ghost'">
        小六壬
      </button>
      <button @click="mode = 'da'" class="flex-1 md:flex-none px-5 py-2 rounded-xl border transition"
              :class="mode === 'da' ? 'bg-ember-500/20 border-ember-500 text-ember-300' : 'btn-ghost'">
        大六壬
      </button>
    </div>

    <BirthInputForm @submit="onSubmit" />

    <div v-if="loading" class="glass p-12 text-center text-ember-300 animate-pulse">起课中…</div>
    <div v-else-if="error" class="glass p-6 border-red-500/40 text-red-300 text-sm">✗ {{ error }}</div>

    <!-- 小六壬展示 -->
    <template v-else-if="mode === 'xiao' && xiao">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div v-for="(v, k) in xiao.san_chuan" :key="k"
             class="glass p-5 text-center border-2"
             :class="guaColor[v.gua]">
          <div class="text-xs text-ink-500 mb-2">{{ k }}</div>
          <div class="font-kai text-4xl tracking-widest mb-2">{{ v.gua }}</div>
          <div class="text-xs space-y-0.5">
            <div>{{ v.五行 }} · {{ v.方位 }}</div>
            <div class="text-ink-500">色: {{ v.色 }}</div>
          </div>
          <div class="text-xs text-slate-300 mt-3 leading-relaxed">{{ v.断 }}</div>
        </div>
      </div>
      <div class="glass p-5 mt-4 border-ember-500/40">
        <div class="text-xs text-ink-500 mb-2">主断（时将）</div>
        <div class="font-kai text-3xl text-ember-400">{{ xiao.primary }}</div>
        <div class="text-sm text-slate-300 mt-2">{{ xiao.primary_meaning?.断 }}</div>
      </div>
    </template>

    <!-- 大六壬展示 -->
    <template v-else-if="mode === 'da' && da">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="glass p-5 space-y-3">
          <h3 class="title-zh">基础信息</h3>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div>日干支：<span class="ganzhi text-lg">{{ da.day_ganzhi }}</span></div>
            <div>占时：<span class="ganzhi text-lg">{{ da.zhan_shi }}</span></div>
            <div>中气：<span class="text-ember-300">{{ da.zhongqi }}</span></div>
            <div>月将：<span class="text-ember-300">{{ da.yue_jiang }}</span></div>
          </div>
        </div>

        <div class="glass p-5">
          <h3 class="title-zh mb-3">三传</h3>
          <div class="grid grid-cols-3 gap-2">
            <div v-for="key in ['初传','中传','末传']" :key="key"
                 class="rounded-md bg-ink-900/40 border border-ember-500/30 p-3 text-center">
              <div class="text-xs text-ink-500 mb-1">{{ key }}</div>
              <div class="ganzhi text-2xl">{{ da.san_chuan[key] }}</div>
            </div>
          </div>
          <div class="text-xs text-ink-500 mt-2">{{ da.san_chuan.method }}</div>
        </div>

        <div class="glass p-5 md:col-span-2">
          <h3 class="title-zh mb-3">四课</h3>
          <div class="grid grid-cols-4 gap-2">
            <div v-for="c in da.four_classes" :key="c.index"
                 class="rounded-md bg-ink-900/40 border border-ink-600/60 p-3 text-center">
              <div class="text-[10px] text-ink-500 mb-1">第{{ c.index }}课 · {{ c.type }}</div>
              <div class="ganzhi text-xl text-ember-300">{{ c.tian }}</div>
              <div class="text-[10px] text-ink-500 my-0.5">天</div>
              <div class="border-t border-ink-600/60 pt-1">
                <div class="text-[10px] text-ink-500 mb-0.5">地</div>
                <div class="ganzhi text-xl text-gold-400">{{ c.di }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="glass p-5 md:col-span-2">
          <h3 class="title-zh mb-3">十二贵神 (昼贵)</h3>
          <div class="grid grid-cols-6 gap-1.5 text-[10px]">
            <div v-for="(shen, zhi) in da.twelve_gui_shen" :key="zhi"
                 class="text-center bg-ink-900/40 border border-ink-600/60 rounded p-1.5">
              <div class="text-ember-300">{{ shen }}</div>
              <div class="text-ink-500">{{ zhi }}</div>
            </div>
          </div>
        </div>
      </div>
      <div class="text-[10px] text-ink-500 italic">{{ da.note }}</div>

      <AnalysisPanel v-if="da.analysis" title="六壬解读"
                     :analysis="da.analysis" accent="mystic" />
    </template>

    <div v-else class="glass p-12 text-center">
      <div class="text-6xl mb-4 opacity-30 font-kai animate-float">六</div>
      <p class="text-slate-400">输入时刻或事件起课时间，开始起课</p>
    </div>
  </div>
</template>
