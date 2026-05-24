/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // 暗黑国潮主色：深玄武 + 朱砂金
        ink: {
          900: '#0a0e16',   // 至深玄
          800: '#10141d',   // 主背景
          700: '#1a1f2c',   // 卡片表面
          600: '#252b3a',   // 边线
          500: '#3a4358',   // 弱文字
        },
        ember: {
          50:  '#fef6f0',
          100: '#fde7d4',
          300: '#f5a96a',
          500: '#e07b3c',   // 主品牌朱砂橙
          600: '#c45828',
          700: '#9c3f1c',
        },
        jade: {
          400: '#7dd3a8',   // 玉色辅助
          500: '#42b685',
        },
        gold: {
          400: '#d4b061',
          500: '#b8924a',
        },
      },
      fontFamily: {
        kai: ['"KaiTi"', '"STKaiti"', 'cursive', 'serif'],
        sans: ['"Inter"', '-apple-system', 'BlinkMacSystemFont', '"PingFang SC"', '"Microsoft YaHei"', 'sans-serif'],
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.36)',
        'glow-ember': '0 0 20px rgba(224, 123, 60, 0.4)',
        'glow-gold': '0 0 16px rgba(212, 176, 97, 0.35)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
    },
  },
  plugins: [],
}
