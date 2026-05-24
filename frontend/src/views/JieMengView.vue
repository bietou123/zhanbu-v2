<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { jiemengAPI } from '@/api/client'

const query = ref('')
const loading = ref(false)
const result = ref<any>(null)
const categories = ref<any>(null)

const hotKeywords = ['蛇','龙','水','火','结婚','怀孕','掉牙','钱','飞','考试']

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  try { result.value = (await jiemengAPI.search(query.value)).data }
  finally { loading.value = false }
}

function quickSearch(k: string) {
  query.value = k
  search()
}

onMounted(async () => {
  categories.value = (await jiemengAPI.categories()).data
})
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="font-kai text-3xl md:text-4xl text-ember-400 tracking-widest">周公解梦</h1>
      <p class="text-sm text-ink-500 mt-1">输入梦境关键词，获取解析</p>
    </div>

    <div class="glass p-5 md:p-6 space-y-3">
      <div class="flex gap-2">
        <input v-model="query" @keyup.enter="search"
               class="input-base flex-1" placeholder="梦见…（如：蛇、龙、掉牙）"/>
        <button @click="search" :disabled="loading || !query" class="btn-primary">
          {{ loading ? '...' : '解' }}
        </button>
      </div>
      <div>
        <div class="text-xs text-ink-500 mb-2">热门</div>
        <div class="flex flex-wrap gap-1.5">
          <button v-for="k in hotKeywords" :key="k" @click="quickSearch(k)"
                  class="px-3 py-1 text-xs rounded-md bg-ink-900/50 border border-ink-600
                         text-slate-300 hover:border-ember-500/50 hover:text-ember-300 transition">
            {{ k }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="result" class="space-y-3">
      <div class="text-xs text-ink-500">
        匹配 {{ result.total_matched }} 条，显示前 {{ result.results.length }} 条
      </div>
      <div v-for="(r, i) in result.results" :key="i"
           class="glass glass-hover p-5 space-y-2">
        <div class="flex justify-between items-baseline">
          <h4 class="font-kai text-xl text-ember-400">{{ r.keywords[0] }}</h4>
          <div class="flex gap-2 items-center text-[10px]">
            <span class="text-jade-400">{{ r.category }}</span>
            <span class="text-ink-500">★ {{ r.score }}</span>
          </div>
        </div>
        <div class="text-xs text-ink-500">
          关联：{{ r.keywords.join(' · ') }}
        </div>
        <p class="text-sm text-slate-200 leading-relaxed">{{ r.interpretation }}</p>
      </div>
      <div v-if="result.results.length === 0"
           class="glass p-8 text-center text-slate-400 text-sm">
        未找到相关梦境，试试其他关键词
      </div>
    </div>

    <div v-else-if="categories" class="glass p-5">
      <h3 class="title-zh mb-3">分类索引 (共 {{ categories.total_entries }} 条)</h3>
      <div class="flex flex-wrap gap-2">
        <span v-for="(cnt, cat) in categories.categories" :key="cat"
              class="px-3 py-1.5 rounded-md bg-ink-900/50 border border-ink-600 text-xs">
          {{ cat }} <span class="text-ember-300">{{ cnt }}</span>
        </span>
      </div>
    </div>
  </div>
</template>
