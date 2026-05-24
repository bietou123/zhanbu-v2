# 詹卜 (Zhanbu) · 一站式玄学分析平台

> 高精度 · 模块化 · 暗黑国潮 · 多端响应式

詹卜是一个集 **八字、紫微斗数、奇门遁甲、六壬、七政四余、梅花易数、占卜起卦、周公解梦** 于一体的现代玄学分析 Web 平台。

- **后端**：Python 3.10+ / FastAPI / `lunar-python` / `pyswisseph`
- **前端**：Vue 3 / TailwindCSS / ECharts
- **核心理念**：排盘 0 容错。严格依赖成熟天文历法库，绝不"硬算"。

---

## 项目结构

```
zhanbu/
├── backend/                       # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/                # REST 路由 (按版本)
│   │   ├── core/                  # 应用配置
│   │   ├── schemas/               # Pydantic 数据契约
│   │   ├── services/              # 各术数业务逻辑
│   │   ├── utils/                 # 历法核心等公共工具
│   │   │   └── calendar_core.py   # 真太阳时 / 公农历 / 干支
│   │   ├── models/                # ORM 模型 (后续接入数据库)
│   │   └── main.py                # FastAPI 入口
│   ├── tests/
│   └── requirements.txt
├── frontend/                      # Vue 3 前端 (Milestone 4 创建)
├── docs/                          # 设计与术数算法文档
├── .gitignore
└── README.md
```

---

## 快速开始（后端）

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

打开 <http://127.0.0.1:8000/docs> 查看自动生成的 OpenAPI 文档。

---

## 🚀 Docker 一键部署（飞牛 NAS / 任何 Linux）

```bash
git clone https://github.com/bietou123/zhanbu-v2.git
cd zhanbu-v2
docker compose up -d --build
```

访问 `http://<host>:8088` 即用。详见 [docs/DEPLOY.md](docs/DEPLOY.md)。

---

## 开发里程碑

- [x] **M1**：基础设施 + 历法核心库（真太阳时、公农历、干支）
- [ ] **M2**：八字 / 紫微斗数 / 奇门遁甲 后端引擎
- [ ] **M3**：六壬 / 七政四余 / 梅花易数 / 占卜起卦 / 周公解梦
- [ ] **M4**：前端响应式 Dashboard（三大盘联动工作台）
- [ ] **M5**：剩余前端模块 + 数据库档案 + 全栈联调

---

## 核心数据契约 (Base Input Schema)

所有术数模块共享同一个排盘入参：

```json
{
  "name": "张三",
  "gender": 1,
  "birth_time": "1990-05-15 14:30:00",
  "is_lunar": false,
  "is_leap_month": false,
  "longitude": 116.40,
  "latitude": 39.90
}
```

---

## License

MIT
