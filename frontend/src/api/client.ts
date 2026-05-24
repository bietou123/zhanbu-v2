import axios from 'axios'

export const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

http.interceptors.response.use(
  (resp) => resp.data,
  (err) => {
    console.error('[API error]', err?.response?.data || err)
    return Promise.reject(err)
  },
)

export interface BirthInput {
  name: string
  gender: 0 | 1
  birth_time: string  // YYYY-MM-DD HH:MM:SS
  is_lunar: boolean
  is_leap_month: boolean
  longitude: number
  latitude: number
}

export interface APIResponse<T = any> {
  code: number
  message: string
  data: T
}

// ============ Calendar ============
export const calendarAPI = {
  resolve: (p: BirthInput) => http.post<any, APIResponse>('/calendar/resolve', p),
  trueSolar: (p: BirthInput) => http.post<any, APIResponse>('/calendar/true_solar_time', p),
}

// ============ 三盘联动 ============
export const dashboardAPI = {
  triple: (p: BirthInput) => http.post<any, APIResponse>('/dashboard/triple_plate', p),
}

// ============ 八字 / 紫微 / 奇门 单盘 ============
export const baziAPI = { compute: (p: BirthInput) => http.post<any, APIResponse>('/bazi/compute', p) }
export const ziweiAPI = { compute: (p: BirthInput) => http.post<any, APIResponse>('/ziwei/compute', p) }
export const qimenAPI = { compute: (p: BirthInput) => http.post<any, APIResponse>('/qimen/compute', p) }

// ============ 七政四余 ============
export const qizhengAPI = { compute: (p: BirthInput) => http.post<any, APIResponse>('/qizheng/compute', p) }

// ============ 六壬 ============
export const liurenAPI = {
  da: (p: BirthInput) => http.post<any, APIResponse>('/liuren/compute', p),
  xiao: (p: BirthInput) => http.post<any, APIResponse>('/xiaoliuren/compute', p),
}

// ============ 占卜起卦 ============
export const divinationAPI = {
  coin: (seed?: number) => http.post<any, APIResponse>('/divination/coin', { seed }),
  numbers: (n1: number, n2: number, n3: number) =>
    http.post<any, APIResponse>('/divination/numbers', { n1, n2, n3 }),
}

// ============ 梅花易数 ============
export const meihuaAPI = {
  byTime: (p: BirthInput) => http.post<any, APIResponse>('/meihua/by_time', p),
  byChars: (part1: string, part2: string) =>
    http.post<any, APIResponse>('/meihua/by_chars', { part1, part2 }),
  byNumbers: (n1: number, n2: number) =>
    http.post<any, APIResponse>('/meihua/by_numbers', { n1, n2 }),
}

// ============ 周公解梦 ============
export const jiemengAPI = {
  search: (q: string, top_k = 5) =>
    http.get<any, APIResponse>('/jiemeng/search', { params: { q, top_k } }),
  categories: () => http.get<any, APIResponse>('/jiemeng/categories'),
}

// ============ 档案 (M5 后端添加) ============
export const profileAPI = {
  list: () => http.get<any, APIResponse>('/profiles'),
  create: (p: BirthInput) => http.post<any, APIResponse>('/profiles', p),
  get: (id: number) => http.get<any, APIResponse>(`/profiles/${id}`),
  remove: (id: number) => http.delete<any, APIResponse>(`/profiles/${id}`),
}
