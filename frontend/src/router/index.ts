import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
    { path: '/qizheng', name: 'qizheng', component: () => import('@/views/QiZhengView.vue') },
    { path: '/liuren', name: 'liuren', component: () => import('@/views/LiuRenView.vue') },
    { path: '/divination', name: 'divination', component: () => import('@/views/DivinationView.vue') },
    { path: '/meihua', name: 'meihua', component: () => import('@/views/MeiHuaView.vue') },
    { path: '/jiemeng', name: 'jiemeng', component: () => import('@/views/JieMengView.vue') },
    { path: '/profiles', name: 'profiles', component: () => import('@/views/ProfilesView.vue') },
  ],
})

export default router
