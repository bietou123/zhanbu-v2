# 詹卜 · 飞牛 NAS 部署指南

部署到飞牛 NAS（fnOS），任何地方通过浏览器访问您自己的算命平台。

---

## 一、部署到 NAS（一次性 5 分钟）

### 方法 A：飞牛 Docker UI 一键部署（推荐 · 不用命令行）

> 飞牛 NAS 自带 Docker 管理界面，支持 docker-compose YAML 粘贴部署。

1. 打开飞牛 NAS 管理后台 → 应用中心 → 安装 **Docker**（如已装跳过）
2. 进入 **Docker → Compose → 新建项目**
3. **项目名**：填 `zhanbu`
4. **路径**：选一个文件夹（如 `/vol1/docker/zhanbu`）。点 **拉取代码**：
   - 仓库地址：`https://github.com/bietou123/zhanbu-v2.git`（或您 Gitea 那个）
   - 分支：`main`
5. **Compose 文件**：自动识别根目录的 `docker-compose.yml`
6. 点 **部署**，等 3-5 分钟首次构建（拉镜像 + npm install + pip install）
7. 完成后浏览器访问 `http://<NAS局域网IP>:8088`，能看到詹卜界面就 OK ✅

### 方法 B：SSH 命令行部署（任何 Linux 都行）

```bash
# 1. SSH 进 NAS
ssh <user>@<NAS-IP>

# 2. 选个目录，拉代码
mkdir -p /vol1/docker && cd /vol1/docker
git clone https://github.com/bietou123/zhanbu-v2.git zhanbu
cd zhanbu

# 3. 一键起
docker compose up -d --build

# 4. 看日志
docker compose logs -f
```

访问：`http://<NAS局域网IP>:8088`

---

## 二、暴露到公网（让自己在任何地方能访问）

### 方案 1：飞牛云（最简单，免费，0 配置） ⭐推荐

飞牛 NAS 自带"飞牛云"远程访问，类似群晖 QuickConnect，**不需要公网 IP**：

1. NAS 后台 → **飞牛云** → 注册 / 登录飞牛账号
2. 在飞牛云 → 远程访问 → 找到 **zhanbu-frontend** 容器（8088 端口）
3. 启用远程访问，分配一个 `xxx.fnnas.cn` 形式的域名
4. 全球任何浏览器打开这个 `xxx.fnnas.cn`，就是您的詹卜

### 方案 2：DDNS + 路由器端口转发（您有公网 IP 时）

如果您家宽带运营商分配了公网 IPv4（电信/联通办过申请），或者您有 IPv6：

1. **路由器端口转发**：
   - 公网 80 / 443 → NAS 内网 IP:8088
2. **DDNS**：
   - 用阿里云域名 DDNS / 花生壳 / 腾讯云 DNSPod
   - 把您的域名（如 `zhanbu.example.com`）解析到您的公网 IP，自动更新
3. **HTTPS 加密**（可选）：
   - 飞牛 NAS 装 Nginx Proxy Manager，申请 Let's Encrypt 证书，反代到 8088

### 方案 3：用您的 arrowwood.top 服务器做反代（推荐进阶）

您已有公网服务器 (`gitea.arrowwood.top`)：

1. 在那台公网服务器上配 nginx，把 `zhanbu.arrowwood.top` 反代到您家 NAS
2. 但要让公网服务器能访问家里 NAS：可以用 **frp / nps / Tailscale** 打通
3. 最稳但配置最复杂

### 方案 4：纯内网穿透（不要公网 IP，简单）

用免费内网穿透服务：

| 服务 | 国内速度 | 免费额度 | 说明 |
|---|---|---|---|
| **Cloudflare Tunnel** | 一般 | 免费 | 全球边缘节点，需要 CF 账号 |
| **Tailscale** | 快 | 免费 100 设备 | P2P 加密通道，需登录 |
| **花生壳** | 中 | 免费有限速 | 国内主流 |
| **frp + 公网 VPS** | 快 | 看 VPS 价 | 自己搭，最稳 |

---

## 三、改完代码怎么升级？

每次您（或我）push 新代码到 GitHub / Gitea，在 NAS 上执行：

```bash
cd /vol1/docker/zhanbu
git pull
docker compose up -d --build
```

或者在飞牛 Docker UI → 项目 → 拉取最新 → 重新部署。

---

## 四、常见问题

**Q：第一次 build 卡在 `pip install` / `npm install`**  
A：国内网络问题。Dockerfile 已经默认走清华 pypi + npmmirror 镜像，正常 3-5 分钟。如果还慢，去 Docker 设置加 docker.io 镜像加速。

**Q：怎么备份档案数据？**  
A：所有用户档案在 `./data/zhanbu-db/zhanbu.db`。复制走这个文件就是完整备份。

**Q：能不能改端口？**  
A：改 `docker-compose.yml` 里 `frontend.ports` 那一行的左边数字（如 `8088:80` → `9999:80`）。

**Q：能不能开 HTTPS？**  
A：自己 NAS 上建议用 Nginx Proxy Manager 反代 + Let's Encrypt 自动证书。

---

## 五、卸载

```bash
cd /vol1/docker/zhanbu
docker compose down            # 停容器
docker compose down -v --rmi all  # 全删 (镜像+卷+网络)
```

数据库文件还在 `./data/zhanbu-db/`，手动 `rm -rf` 删掉即可。
