<script setup lang="ts">
defineProps<{
  title?: string
  analysis: Record<string, any>
  accent?: 'ember' | 'cyber' | 'mystic'
}>()

function flatten(obj: any, prefix = ''): { key: string; value: string }[] {
  const out: { key: string; value: string }[] = []
  if (obj == null || obj === '') return out
  if (typeof obj === 'string' || typeof obj === 'number' || typeof obj === 'boolean') {
    out.push({ key: prefix || 'item', value: String(obj) })
    return out
  }
  if (Array.isArray(obj)) {
    if (obj.length === 0) return out
    const arr = obj.map((x) =>
      typeof x === 'object' ? JSON.stringify(x, null, 0) : String(x),
    )
    out.push({ key: prefix || 'list', value: arr.join(' / ') })
    return out
  }
  for (const [k, v] of Object.entries(obj)) {
    if (v == null || v === '') continue
    if (typeof v === 'object' && !Array.isArray(v)) {
      out.push(...flatten(v, k))
    } else {
      out.push(...flatten(v, k))
    }
  }
  return out
}

const labelMap: Record<string, string> = {
  summary: '总览',
  personality: '性格特质',
  career: '事业格局',
  career_advice: '事业建议',
  love: '感情婚姻',
  love_advice: '感情指引',
  wealth_health: '财运 · 健康',
  current_yun_hint: '当前大运',
  judgement: '判断',
  xi_yong_shen: '喜用神',
  ji_shen: '忌神',
  advice: '建议',
  auspicious_directions: '吉方',
  auspicious_colors: '吉色',
  palace_focus: '关键宫位',
  si_hua_year: '年干四化',
  shen_gong_hint: '身宫提示',
  best_palace: '最吉方位',
  worst_palace: '避忌方位',
  ushen_advice: '用神指引',
  overall: '综合',
  chu_chuan: '初传',
  zhong_chuan: '中传',
  mo_chuan: '末传',
  principle: '原理',
  gui_shen_hint: '贵神提示',
  sun: '太阳',
  moon: '太阴',
  venus: '金星',
  mars: '火星',
  four_yu_hint: '四余提示',
  ben_judgement: '本卦辞',
  bian_judgement: '变卦辞',
  hu_judgement: '互卦辞',
  moving_yao: '动爻',
  ti_yong_detail: '体用详断',
  is_lucky: '吉否',
  ben_gua_advice: '本卦解',
  hu_gua_advice: '互卦解',
  bian_gua_advice: '变卦解',
  ying_qi_hint: '应期',
  zodiac: '星座',
  trait: '星性',
  zodiac_trait: '星座特征',
  element: '元素 / 模式',
  xiu: '星宿',
  longitude: '黄经',
  compose: '格局',
  direction: '方位',
  palace: '宫位',
  bagua: '八卦',
}
</script>

<template>
  <div class="analysis-card glass-neon">
    <div class="flex items-center justify-between">
      <div class="title-cyber flex items-center gap-2">
        <span :class="accent === 'cyber' ? 'seal-cyber' : 'seal'">解</span>
        <span>{{ title || 'AI 分析' }}</span>
      </div>
      <span class="chip">RULE-BASED · v0.1</span>
    </div>

    <div v-if="analysis.summary"
         class="text-sm md:text-base text-slate-100 leading-relaxed font-kai
                px-3 py-2 rounded-lg
                bg-gradient-to-r from-cyber-500/10 via-ember-500/10 to-mystic-500/10
                border-l-2 border-cyber-400/70">
      {{ analysis.summary }}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
      <div v-for="(item, i) in flatten(analysis).filter(x => x.key !== 'summary' && x.value)"
           :key="i"
           class="rounded-lg bg-ink-900/40 border border-ink-600/40
                  px-3 py-2 hover:border-cyber-400/40 transition">
        <div class="label">{{ labelMap[item.key] || item.key }}</div>
        <div class="text-xs md:text-sm text-slate-200 mt-0.5 leading-relaxed">{{ item.value }}</div>
      </div>
    </div>
  </div>
</template>
