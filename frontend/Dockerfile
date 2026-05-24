# ===== Stage 1: 构建 =====
FROM node:22-alpine AS builder

WORKDIR /build

# 国内 npm 镜像
RUN npm config set registry https://registry.npmmirror.com

COPY package.json package-lock.json* ./
RUN npm ci --no-fund --no-audit

COPY . .
RUN npm run build

# ===== Stage 2: nginx 静态托管 =====
FROM nginx:1.27-alpine

ENV TZ=Asia/Shanghai

RUN apk add --no-cache tzdata curl \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 自定义 nginx 配置（含 /api 反代到 backend 容器）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 拷构建产物
COPY --from=builder /build/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
