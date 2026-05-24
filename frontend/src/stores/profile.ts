import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { BirthInput } from '@/api/client'

const STORAGE_KEY = 'zhanbu:lastInput'

function loadFromStorage(): BirthInput {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {/* ignore */}
  return {
    name: '示例',
    gender: 1,
    birth_time: '1990-05-15 14:30:00',
    is_lunar: false,
    is_leap_month: false,
    longitude: 116.40,
    latitude: 39.90,
  }
}

export const useInputStore = defineStore('input', () => {
  const input = ref<BirthInput>(loadFromStorage())

  function save(v: BirthInput) {
    input.value = { ...v }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(input.value))
  }

  return { input, save }
})
