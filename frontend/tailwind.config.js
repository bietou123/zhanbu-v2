/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // 暗黑国潮 + 赛博朋克双轨配色
        ink: {
          950: '#05070d',
          900: '#0a0e16',
          800: '#10141d',
          700: '#1a1f2c',
          600: '#252b3a',
          500: '#3a4358',
        },
        // 主色：朱砂金 (国潮)
        ember: {
          50:  '#fef6f0', 100: '#fde7d4', 300: '#f5a96a',
          500: '#e07b3c', 600: '#c45828', 700: '#9c3f1c',
        },
        // 高科技青 (cyber)
        cyber: {
          50:  '#ecfeff', 100: '#cffafe',
          300: '#67e8f9', 400: '#22d3ee',
          500: '#06b6d4', 600: '#0891b2', 700: '#0e7490',
        },
        // 紫色辅助 (神秘感)
        mystic: {
          400: '#a78bfa', 500: '#8b5cf6', 600: '#7c3aed',
        },
        jade: { 400: '#7dd3a8', 500: '#42b685' },
        gold: { 400: '#d4b061', 500: '#b8924a' },
      },
      fontFamily: {
        kai:  ['"KaiTi"', '"STKaiti"', 'cursive', 'serif'],
        mono: ['"Fira Code"', '"JetBrains Mono"', 'Menlo', 'Consolas', 'monospace'],
        sans: ['"Inter"', '"PingFang SC"', '"Microsoft YaHei"', 'sans-serif'],
      },
      backdropBlur: { xs: '2px' },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.36)',
        'glow-ember': '0 0 20px rgba(224, 123, 60, 0.4)',
        'glow-cyber': '0 0 24px rgba(34, 211, 238, 0.45)',
        'glow-gold': '0 0 16px rgba(212, 176, 97, 0.35)',
        'glow-mystic': '0 0 24px rgba(167, 139, 250, 0.4)',
        'neon': '0 0 8px currentColor, 0 0 16px currentColor',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'spin-slow': 'spin 18s linear infinite',
        'shimmer': 'shimmer 3s linear infinite',
        'scan': 'scan 4s ease-in-out infinite',
        'fade-up': 'fadeUp 0.5s ease-out',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        scan: {
          '0%, 100%': { transform: 'translateY(-100%)', opacity: '0' },
          '50%': { transform: 'translateY(100%)', opacity: '1' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        glowPulse: {
          '0%, 100%': { filter: 'drop-shadow(0 0 4px currentColor)' },
          '50%': { filter: 'drop-shadow(0 0 12px currentColor)' },
        },
      },
    },
  },
  plugins: [],
}
