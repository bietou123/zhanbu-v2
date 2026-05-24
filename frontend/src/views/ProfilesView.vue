<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { profileAPI, type BirthInput } from '@/api/client'
import BirthInputForm from '@/components/BirthInputForm.vue'
import { useInputStore } from '@/stores/profile'

const list = ref<any[]>([])
const loading = ref(false)
const showForm = ref(false)
const store = useInputStore()

async function refresh() {
  loading.value = true
  try { list.value = (await profileAPI.list()).data || [] }
  finally { loading.value = false }
}

async function save(p: BirthInput) {
  await profileAPI.create(p)
  showForm.value = false
  await refresh()
}

async function remove(id: number) {
  if (!confirm('删除此档案？')) return
  await profileAPI.remove(id)
  await refresh()
}

function applyToInput(p: any) {
  store.save({
    name: p.name, gender: p.gender, birth_time: p.birth_time,
    is_lunar: p.is_lunar, is_leap_month: p.is_leap_month,
    longitude: p.longitude, latitude: p.latitude,
  })
  alert(`已加载档案：${p.name}\n切换到任意排盘页即可使用`)
}

onMounted(refresh)
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-end flex-wrap gap-3">
      <div>
        <h1 class="font-kai text-3xl md:text-4xl text-ember-400 tracking-widest">我的档案</h1>
        <p class="text-sm text-ink-500 mt-1">本地 SQLite 存储 · 一键调用</p>
      </div>
      <button @click="showForm = !showForm" class="btn-primary">
        {{ showForm ? '关闭' : '+ 新建' }}
      </button>
    </div>

    <BirthInputForm v-if="showForm" @submit="save" />

    <div v-if="loading" class="glass p-8 text-center text-ember-300 animate-pulse">加载中…</div>

    <div v-else-if="list.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="p in list" :key="p.id" class="glass glass-hover p-5 space-y-2">
        <div class="flex justify-between items-start">
          <div>
            <div class="font-kai text-xl text-ember-300">{{ p.name }}</div>
            <div class="text-xs text-ink-500">
              {{ p.gender === 1 ? '乾男' : '坤女' }}
              <span v-if="p.is_lunar" class="ml-1 text-jade-400">[农]</span>
            </div>
          </div>
          <span class="text-[10px] text-ink-500">#{{ p.id }}</span>
        </div>
        <div class="text-xs text-slate-300 font-mono">{{ p.birth_time }}</div>
        <div class="text-xs text-ink-500">
          ({{ p.longitude }}, {{ p.latitude }})
        </div>
        <div v-if="p.note" class="text-xs text-slate-400 italic pt-1 border-t border-ink-600/40">
          {{ p.note }}
        </div>
        <div class="flex gap-2 pt-2">
          <button @click="applyToInput(p)" class="flex-1 btn-ghost text-xs">载入</button>
          <button @click="remove(p.id)" class="btn-ghost text-xs text-red-400 hover:bg-red-500/10">
            删除
          </button>
        </div>
      </div>
    </div>

    <div v-else class="glass p-12 text-center">
      <div class="text-6xl mb-4 opacity-30 font-kai animate-float">⌘</div>
      <p class="text-slate-400">尚无档案，点击「新建」开始</p>
    </div>
  </div>
</template>
