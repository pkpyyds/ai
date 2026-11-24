# Meridian · AI 跨境电商项目框架

本仓库包含**可独立打开的交互原型**和 Vue3 + FastAPI + PostgreSQL 的演示框架。它不是已交付的完整生产系统：详细设计和用例的质量门禁仍未通过，详见 [自检报告](docs/self-check-report.md)。

## 1. 先查看可点击原型

直接用浏览器打开 [`prototype/index.html`](prototype/index.html)，无需安装或网络。侧栏可切换工作台、商品池、候选池、内容生成、审核、上架、规则和任务页面；可搜索商品并体验初核→复核→模拟内容审核→上架任务流程。示例仅保存在页面会话中，刷新即重置。所有图表、商品、价格及结果都是虚构示例，不执行采集、侵权检查、模型调用或上架。`frontend/public/prototype/index.html` 是用于 Web 发布的副本，修改原型后请同步复制。

## 2. 框架已实现与未实现

- 后端按 **Controller/API Router → Service → Repository → Model/Schema** 分层；前端使用 **View/Component/Pinia Store/API/Router**。`adapters/contracts.py` 仅定义外部依赖替换边界。
- 框架已实现本地演示数据库、商品池/候选池查询、两阶段人工核验、审核意见校验、条件状态更新、审计记录、复核后创建 `PENDING` 内容任务。复核后**没有生成内容**。数据库迁移为演示骨架，并非生产数据契约。`services/selection.py` 提供独立的 OR 条件函数及单元测试，未接入实际测算或入池；阈值相等时通过是待确认的设计假设。
- 未实现认证鉴权、真实租户隔离、接口幂等键、完整规则/货源/利润/侵权、爬虫、模型、内容审核和上架等业务功能；相关页面只是入口或原型。不得用于真实商品或生产环境。演示接口默认关闭；`APP_DEMO_MODE=true` 仅用于本地隔离环境，固定租户 1，无登录鉴权。
- 用户确认的主线、假设及仍需确认的问题见 [需求分析](docs/requirements-analysis.md)、[概要设计](docs/overview-design.md)、[详细设计](docs/detailed-design.md) 和 [测试用例](docs/test-cases.md)。
- 公开数据不代表可合法采集。合规开关默认关闭，未实现任何外部采集；即使设置 `CRAWL_ENABLED=true` 也不能启用采集；侵权、置信度、供应商 API、模型能力、上架方式均不作保证。

## 3. Docker 本地演示（PostgreSQL）

需要 Docker 和 Compose。示例账号密码仅供本机演示，不要用在生产环境。首次启动并显式打开演示模式：

```sh
APP_DEMO_MODE=true docker compose up --build -d
APP_DEMO_MODE=true docker compose exec api python -m app.seed
```

访问 `http://localhost:8080/`，独立原型位于 `/prototype/index.html`。API 使用相对 `/api` 经 Nginx 反代；可通过 `/api/v1/health` 检查服务；开发模式直接访问后端 `/docs` 可查看演示 API，Compose 的 Nginx 未对外暴露该页面。演示模式无认证；Compose 默认只绑定本机回环地址，请勿将端口暴露给不可信网络。

`docker compose down` 停止；数据持久化在 `postgres_data` 卷。若不指定 `APP_DEMO_MODE=true`，业务接口默认 503。测试样本重复运行不会重复插入。默认连接配置仅为本地开发，生产的凭证、TLS、认证等未设计完成。

## 4. 无 Docker 本地开发

准备 Python 3.11、Node.js 20+ 和 PostgreSQL。也可用 SQLite 进行本地演示/测试（不是生产数据库）：

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
cd backend
export DATABASE_URL=sqlite:///./demo.db  # 改为 postgresql+psycopg://... 可使用 PostgreSQL
export APP_DEMO_MODE=true
alembic upgrade head
python -m app.seed
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

另开终端：

```sh
cd frontend
npm ci
npm run dev
```

Vite 默认 `http://localhost:5173/`；其 `/api` 代理到服务端的 `127.0.0.1:8000`，浏览器只使用相对路径。可通过服务端环境变量 `API_PROXY_TARGET` 修改代理目标。正式部署需要独立完成身份、权限和配置管理，不可复用演示模式。

## 5. 验证

```sh
cd backend && ../.venv/bin/pytest -q
cd ../frontend && npm run build
```

测试使用内存 SQLite，验证 OR 组合及边界、两阶段流转、重复审核冲突、驳回及默认关闭；不代表 PostgreSQL、外部集成、安全或业务验收已通过。
