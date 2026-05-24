<script setup lang="ts">
import { reactive, watch } from 'vue'
import { useInputStore } from '@/stores/profile'
import type { BirthInput } from '@/api/client'

const props = defineProps<{ initial?: Partial<BirthInput>; compact?: boolean }>()
const emit = defineEmits<{ (e: 'submit', v: BirthInput): void }>()

const store = useInputStore()
const form = reactive<BirthInput>({ ...store.input, ...(props.initial || {}) })

// 把日期+时间拆开方便手机端原生 picker
const dateTime = reactive({
  date: form.birth_time.split(' ')[0] || '1990-05-15',
  time: form.birth_time.split(' ')[1] || '14:30:00',
})

watch(dateTime, () => {
  form.birth_time = `${dateTime.date} ${dateTime.time}`
})

function submit() {
  const seconds = dateTime.time.split(':').length === 2 ? `${dateTime.time}:00` : dateTime.time
  form.birth_time = `${dateTime.date} ${seconds}`
  store.save(form)
  emit('submit', { ...form })
}

// 常用城市快速定位
const cities = [
  { name: '北京',   lng: 116.40, lat: 39.90 },
  { name: '上海',   lng: 121.47, lat: 31.23 },
  { name: '广州',   lng: 113.27, lat: 23.13 },
  { name: '深圳',   lng: 114.06, lat: 22.55 },
  { name: '杭州',   lng: 120.16, lat: 30.29 },
  { name: '成都',   lng: 104.06, lat: 30.67 },
  { name: '武汉',   lng: 114.30, lat: 30.59 },
  { name: '西安',   lng: 108.94, lat: 34.34 },
  { name: '南京',   lng: 118.78, lat: 32.04 },
  { name: '重庆',   lng: 106.55, lat: 29.56 },
]
function pickCity(c: { lng: number; lat: number }) {
  form.longitude = c.lng
  form.latitude = c.lat
}
</script>

<template>
  <form @submit.prevent="submit"
        class="glass p-5 md:p-6 space-y-4"
        :class="{ 'space-y-3': compact }">
    <h3 class="title-zh flex items-center gap-2">
      <span class="seal text-sm">辰</span>生辰信息
    </h3>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 md:gap-4">
      <label class="block">
        <span class="text-xs text-ink-500 mb-1 block">姓名</span>
        <input v-model="form.name" class="input-base" placeholder="姓名 / 化名" />
      </label>

      <label class="block">
        <span class="text-xs text-ink-500 mb-1 block">性别</span>
        <div class="flex gap-2">
          <button type="button"
                  @click="form.gender = 1"
                  class="flex-1 py-2.5 rounded-xl border transition"
                  :class="form.gender === 1
                    ? 'bg-ember-500/20 border-ember-500/60 text-ember-300'
                    : 'bg-ink-900/40 border-ink-600 text-slate-400 hover:text-white'">
            乾 · 男
          </button>
          <button type="button"
                  @click="form.gender = 0"
                  class="flex-1 py-2.5 rounded-xl border transition"
                  :class="form.gender === 0
                    ? 'bg-ember-500/20 border-ember-500/60 text-ember-300'
                    : 'bg-ink-900/40 border-ink-600 text-slate-400 hover:text-white'">
            坤 · 女
          </button>
        </div>
      </label>

      <label class="block">
        <span class="text-xs text-ink-500 mb-1 block">出生日期</span>
        <input v-model="dateTime.date" type="date" class="input-base" />
      </label>

      <label class="block">
        <span class="text-xs text-ink-500 mb-1 block">出生时刻 (24h)</span>
        <input v-model="dateTime.time" type="time" step="1" class="input-base" />
      </label>

      <label class="flex items-center gap-2 col-span-1 md:col-span-2">
        <input v-model="form.is_lunar" type="checkbox" class="w-4 h-4 accent-ember-500" />
        <span class="text-sm text-slate-300">该日期为农历</span>
        <template v-if="form.is_lunar">
          <span class="mx-2 text-ink-500">·</span>
          <input v-model="form.is_leap_month" type="checkbox" class="w-4 h-4 accent-ember-500" />
          <span class="text-sm text-slate-300">闰月</span>
        </template>
      </label>

      <label class="block">
        <span class="text-xs text-ink-500 mb-1 block">出生地经度</span>
        <input v-model.number="form.longitude" type="number" step="0.01" class="input-base" />
      </label>

      <label class="block">
        <span class="text-xs text-ink-500 mb-1 block">出生地纬度</span>
        <input v-model.number="form.latitude" type="number" step="0.01" class="input-base" />
      </label>
    </div>

    <div>
      <div class="text-xs text-ink-500 mb-2">常用城市</div>
      <div class="flex flex-wrap gap-1.5">
        <button v-for="c in cities" :key="c.name"
                type="button" @click="pickCity(c)"
                class="px-3 py-1 text-xs rounded-md
                       bg-ink-900/50 border border-ink-600 text-slate-300
                       hover:border-ember-500/50 hover:text-ember-300 transition">
          {{ c.name }}
        </button>
      </div>
    </div>

    <button type="submit" class="btn-primary w-full md:w-auto">
      <span class="font-kai mr-1">起</span>盘
    </button>
  </form>
</template>
