# 详细设计说明书

> 项目：AI 跨境电商（选品分析 Agent + 商品内容生成 Agent）
> 版本：v1.2（2026-11-24 门禁修订，未通过）
> 前置：需求分析（BR-001~BR-028、A-01~A-14）、概要设计
> 更新：爬取公开数据；利润公式/汇率前端可配置；侵权查专利+商标；亚马逊上架未定；模型服务预留配置项。
> 定位：指导开发与测试；不写完整源码；伪代码接近实现但非完整代码。

---

## 1. 文档信息

### 1.1 目的

将概要设计展开为可开发、可测试的详细设计：模块、表、接口、状态机、伪代码、前端、非功能、部署。

### 1.2 范围与读者

- 范围：本期 S-01~S-10（见需求分析第 2 章）。
- 读者：前端/后端开发、测试、运维、运营代表。

### 1.3 术语

| 术语 | 说明 |
|---|---|
| 商品池 | 利润通过且专利与商标均未检出风险的待核验商品集合；不构成法律结论 |
| 候选池 | 初核通过的待复核商品集合 |
| 审核逻辑 | 运营可编辑的内容审核规则集（版本化） |
| 适配器 | 隔离外部依赖（爬虫/模型/上架）的接口层 |
| 幂等键 | 客户端生成的唯一请求标识，用于去重 |

### 1.4 版本与参考

| 版本 | 说明 |
|---|---|
| v1.0 | 评审稿，含假设/待确认 |
| v1.1 | 2026-11-24 用户确认更新（公开数据/可配置公式汇率/专利+商标/上架未定/模型预留配置） |
| v1.2 | 2026-11-24 门禁修订：修正伪代码和安全兜底；缺口见自检报告 |

参考：需求分析、概要设计；第 7 章为接口草案，OpenAPI 尚未交付。

---

## 2. 设计范围与需求追溯

### 2.1 追溯矩阵（需求→设计→测试要点）

| 需求 | 设计章节 | 接口 | 数据表 | 测试要点 |
|---|---|---|---|---|
| BR-001~BR-003 | 5.1、8.1 | 采集接口 | products、crawl_tasks | 去重、完整性 |
| BR-004~BR-006、BR-028 | 5.1、8.1~8.2 | 筛选规则接口 | selection_rules、profit_calculations | OR 逻辑、公式/汇率可配置、版本冻结 |
| BR-007~BR-008 | 5.1、8.3 | 侵权校验（专利+商标） | infringement_checks | 双维度拦截、展示条件 |
| BR-009~BR-010 | 5.2、8.4 | 核验接口 | review_tasks | 两阶段、回退 |
| BR-011~BR-015 | 5.3、8.5 | 审核逻辑/内容审核/上架 | audit_rules、content_jobs、listing_jobs | 版本回滚、终审 |
| BR-016~BR-018 | 5.4、8.6 | 采集接口 | crawl_tasks、crawl_raw_payloads | 合规开关、失败队列 |
| BR-019~BR-023 | 5.5、9 | 通用 | idempotency_keys、agent_runs | 幂等、并发、成本 |
| BR-024~BR-027 | 5.6、9、10 | 通用 | audit_logs、tenants | 隔离、审计、注入 |

### 2.2 用例、接口、表清单

- 用例图：`docs/attachments/usecase-selection.mmd`、`docs/attachments/usecase-content.mmd`
- 接口清单：附录 B；数据表清单：附录 C；错误码清单：附录 D。

---

## 3. 总体设计概述

### 3.1 上下文与部署单元

- 前端：Vue3 SPA（Nginx 托管静态）。
- 后端：FastAPI 单体（Uvicorn），内含 Controller/Service/Repository；采集 Worker、Agent Worker 独立进程/容器。
- 数据：PostgreSQL（业务+审计）；原始爬虫数据落库（对象存储待确认 A-11）。

### 3.2 前后端职责边界

- 前端：展示、表单校验、状态管理、错误提示；不做业务判定。
- 后端：全部业务规则、状态流转、规则执行、Agent 编排。

### 3.3 核心数据流

见需求分析第 6.2 节；详细流转见第 8 章伪代码。

### 3.4 MVC 分层决策

- Controller：仅校验/鉴权/封装；Service：业务与事务；Repository：数据访问；Model/Schema：契约。
- 禁止 Controller 直连 DB、禁止业务逻辑在 Controller（概要设计第 4.3 节）。

---

## 4. 用例图

- 选品分析用例图：`docs/attachments/usecase-selection.mmd`
- 内容生成用例图：`docs/attachments/usecase-content.mmd`

> 图源见 [选品用例](attachments/usecase-selection.mmd) 与 [内容用例](attachments/usecase-content.mmd)。图源使用流程图示意系统边界和 include/extend，非 UML 原生用例图，尚需语义验证；导出图尚未生成，不得视为已交付。核心结论：两阶段核验后才能生成，运营编辑规则，人工审核后才能创建上架任务。

---

## 5. 模块详细设计

### 5.1 选品分析 Agent

**职责边界**：采集公开数据→匹配→测算（可配置公式/汇率）→筛选→侵权（专利+商标）→商品池；不处理内容生成。
**依赖**：采集适配层（公开数据）、规则配置（公式/汇率/阈值）、侵权服务（专利+商标）、审核工作流（核验任务）。
**类图**：[选品类图源](attachments/class-selection.mmd)，展示分层调用与商品、货源、规则的关系。
**时序图**：[选品时序图源](attachments/sequence-selection.mmd)，展示失败拦截、两阶段核验和事务边界。

关键成功路径：

1. 创建采集任务 → 适配器抓取公开数据 → 质量校验 → 落库商品。
2. 匹配 1688 货源 → 利润测算（公式版本+汇率快照+规则版本）→ 专利/商标侵权校验 → 双通过则进入商品池。
3. 创建初核任务 → 人工通过 → 进入候选池。

异常路径：采集失败→失败队列；无货源→待补数据；规则不通过→拦截；侵权→拦截；均需记录原因。

事务/幂等/并发：采集以（平台+商品ID）去重；测算以（商品+规则版本）幂等；池流转以状态机守卫 + 乐观锁防并发。

### 5.2 审核工作流（两阶段核验）

**职责**：初核（池→候选）、复核（候选→内容生成），含分发、SLA、驳回回退（回退策略待确认 A-06）。
**时序**：见 `docs/attachments/sequence-selection.mmd` 后半段。

### 5.3 商品内容生成 Agent

**职责**：生成内容→自动审核（审核逻辑版本）→人工审核→上架任务。
**依赖**：编排层、模型服务（预留配置项 A-09）、知识库、审核逻辑。
**类图**：[内容类图源](attachments/class-content.mmd)，展示分层及内容、审核和上架关系。
**时序图**：[内容时序图源](attachments/sequence-content.mmd)，展示生成、审核、失败转人工和上架任务。

关键路径：复核通过→创建内容任务→Agent 生成→自动审核→人工审核→上架任务。
异常：模型超时/低置信或无可信置信度→转人工；自动审核失败→人工审核；人工驳回→终止/重生成（策略待确认）。

### 5.4 采集适配层

**职责**：卖家精灵/1688 公开数据适配器、限流、重试、失败队列、质量校验、合规开关（BR-016）。
**接口**：`CrawlerAdapter.fetch(params) -> RawPayload`；`QualityValidator.validate(payload) -> Result`。
**合规**：仅爬取公开数据；开关关闭、robots 禁止、超限时禁止采集；不实现绕过（A-02）。

### 5.5 编排层与可观测性

**职责**：步骤编排、工具调用、重试/降级、Token 成本、追踪。
**降级**：模型超限→排队/转人工；采集超限→暂停（BR-021）。

### 5.6 权限租户与审计

**职责**：RBAC、租户隔离、审计留痕（BR-024、BR-025）。
**隔离**：所有查询强制 `tenant_id`；越权拒绝并审计。

---

## 6. 数据库表设计

> 约定：主键 `id`（BIGINT/UUID 待确认）、`tenant_id`（A-10）、审计字段 `created_at/updated_at/created_by/updated_by`、软删除 `deleted_at`（核心表适用）。

### 6.1 核心表总览

| 表名 | 用途 | 关键字段 |
|---|---|---|
| tenants | 租户 | id、name、status |
| users | 用户 | id、tenant_id、username、role_id |
| roles | 角色 | id、code、name |
| products | 商品主表（池流转） | id、tenant_id、platform、platform_product_id、title、category、price、sales_volume、status、pool_stage |
| supplier_offers | 1688 货源 | id、product_id、supplier、cost、moq、confidence |
| profit_calculations | 利润测算快照 | id、product_id、rule_version_id、formula_version、fx_snapshot(JSONB)、inputs(JSONB)、result、passed |
| infringement_checks | 侵权校验（专利+商标） | id、product_id、patent_conclusion、trademark_conclusion、overall_conclusion、evidence |
| selection_rules | 筛选规则（含公式/汇率配置） | id、tenant_id、name、formula(JSONB)、fx_config(JSONB)、thresholds(JSONB)、version、status |
| review_tasks | 核验任务 | id、product_id、stage、reviewer_id、conclusion、comment、sla_deadline |
| content_jobs | 内容任务 | id、product_id、prompt_version_id、model、token_usage、status |
| content_artifacts | 生成内容 | id、job_id、title、description、selling_points、confidence |
| audit_rules | 审核逻辑 | id、tenant_id、name、checks(JSONB)、version、status |
| audit_runs | 自动审核记录 | id、artifact_id、rule_version_id、findings(JSONB)、conclusion |
| listing_jobs | 上架任务 | id、product_id、artifact_id、platform、status、receipt |
| crawl_tasks | 采集任务 | id、platform、adapter、status、failure_reason |
| crawl_raw_payloads | 原始数据 | id、task_id、payload(JSONB) |
| agent_runs | Agent 运行 | id、job_id、steps(JSONB)、cost、duration |
| idempotency_keys | 幂等键 | key、scope、result_ref |
| audit_logs | 审计日志 | id、actor、action、target、before/after |

### 6.2 关键表字段与约束（示例）

**products**

| 字段 | 类型 | 约束 |
|---|---|---|
| id | BIGINT | PK |
| tenant_id | BIGINT | NOT NULL，索引 |
| platform | VARCHAR(32) | NOT NULL |
| platform_product_id | VARCHAR(128) | NOT NULL，联合唯一（tenant_id, platform, platform_product_id） |
| title | VARCHAR(512) | NOT NULL |
| price | NUMERIC(12,2) | >=0 |
| sales_volume | BIGINT | >=0 |
| status | VARCHAR(32) | 枚举见 6.4 |
| pool_stage | VARCHAR(32) | 枚举：POOL/CANDIDATE/CONTENT_GEN |

**selection_rules**

| 字段 | 类型 | 约束 |
|---|---|---|
| id | BIGINT | PK |
| tenant_id | BIGINT | NOT NULL |
| name | VARCHAR(128) | NOT NULL |
| formula | JSONB | 利润公式（成本口径/费用项，运营可编辑） |
| fx_config | JSONB | 汇率配置（币种/汇率值/来源/时点，运营可编辑） |
| thresholds | JSONB | 含单品毛利阈值、月销售额阈值、周期 |
| version | INTEGER | NOT NULL，版本递增 |
| status | VARCHAR(16) | DRAFT/PUBLISHED/ROLLED_BACK |

**audit_rules**：结构同上，`checks` 含检查项与阈值。

### 6.2.1 未完成的持久化契约

上述仅为字段草案，`review_tasks.status`、幂等请求哈希与租户/范围唯一约束、Prompt/知识库版本与模型调用日志等尚无完整表定义；接口与表不具备完整可实现性，触发 V-08。字段、关系、租户复合外键与迁移必须冻结后方可开发。

### 6.3 关键 DDL 示例（仅示例，非完整）

```sql
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  tenant_id BIGINT NOT NULL,
  platform VARCHAR(32) NOT NULL,
  platform_product_id VARCHAR(128) NOT NULL,
  title VARCHAR(512) NOT NULL,
  status VARCHAR(32) NOT NULL,
  pool_stage VARCHAR(32) NOT NULL DEFAULT 'POOL',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at TIMESTAMPTZ,
  UNIQUE (tenant_id, platform, platform_product_id)
);
CREATE INDEX idx_products_tenant_status ON products (tenant_id, status);
```

### 6.4 枚举与状态机

- `products.status`：COLLECTED、MATCHED、PROFIT_CALCULATED、INFRINGEMENT_CHECKED、IN_POOL、FIRST_REVIEW_PENDING、CANDIDATE、SECOND_REVIEW_PENDING、CONTENT_GEN_PENDING、REJECTED、ARCHIVED。
- `content_jobs.status`：PENDING、RUNNING、CONTENT_READY、AUDIT_PENDING、HUMAN_REVIEW_PENDING、APPROVED、REJECTED、FAILED。
- `listing_jobs.status`：PENDING、RUNNING、LISTED、FAILED。
- 状态图：`docs/attachments/state-product.mmd`、`docs/attachments/state-content.mmd`、`docs/attachments/state-listing.mmd`。

### 6.5 索引场景、生命周期、迁移

- 索引：租户+状态、平台商品ID、任务状态、创建时间。
- 生命周期：原始数据保留期待确认；审计日志长期保留。
- 迁移：Alembic 版本化；禁止手动改表。

---

## 7. 接口设计

> 统一约定：基路径 `/api/v1`；鉴权 `Authorization: Bearer <token>`；幂等 `Idempotency-Key`；分页 `page/page_size`；统一响应 `{code, message, data}`；错误码见附录 D；OpenAPI 尚未产出或冻结，不能声称与其一致。

### 7.1 通用

| 接口 | 方法 | 路径 | 鉴权 | 说明 |
|---|---|---|---|---|
| 商品池列表 | GET | /api/v1/products/pool | 登录 | 分页/过滤/排序 |
| 商品详情 | GET | /api/v1/products/{id} | 登录 | 含货源/测算/侵权 |
| 候选列表 | GET | /api/v1/products/candidates | 登录 | 同上 |
| 核验通过 | POST | /api/v1/reviews/{taskId}/approve | 审核员 | 幂等 |
| 核验驳回 | POST | /api/v1/reviews/{taskId}/reject | 审核员 | 需意见 |
| 筛选规则列表 | GET | /api/v1/selection-rules | 运营 | 含版本 |
| 创建规则 | POST | /api/v1/selection-rules | 运营 | 草稿 |
| 发布规则 | POST | /api/v1/selection-rules/{id}/publish | 运营 | 版本递增 |
| 回滚规则 | POST | /api/v1/selection-rules/{id}/rollback | 运营 | 审计 |
| 创建采集任务 | POST | /api/v1/crawl-tasks | 运营/系统 | 异步 |
| 查询采集任务 | GET | /api/v1/crawl-tasks/{id} | 登录 | 状态 |
| 创建内容任务 | POST | /api/v1/content-jobs | 系统/运营 | 异步 |
| 查询内容任务 | GET | /api/v1/content-jobs/{id} | 登录 | 含 Token |
| 审核逻辑列表 | GET | /api/v1/audit-rules | 运营 | 含版本 |
| 创建审核逻辑 | POST | /api/v1/audit-rules | 运营 | 创建草稿 |
| 发布/回滚审核逻辑 | POST | /api/v1/audit-rules/{id}/publish、/rollback | 运营 | 同上 |
| 内容审核通过/驳回 | POST | /api/v1/content-reviews/{id}/approve、/reject | 内容审核员 | 终审 |
| 创建上架任务 | POST | /api/v1/listing-jobs | 上架操作员 | 方式未定，暂定人工确认 |
| 查询上架任务 | GET | /api/v1/listing-jobs/{id} | 登录 | 回执 |
| 审计日志 | GET | /api/v1/audit-logs | 审计员 | 只读 |
| 成本查询 | GET | /api/v1/agent-costs | 运营/审计 | Token/费用 |

### 7.2 请求/响应示例（节选；其余接口的 schema、示例和错误码尚未完成）

**核验通过**

- 请求：`POST /api/v1/reviews/101/approve`，头 `Idempotency-Key: <uuid>`，体 `{comment: "符合"}`。
- 响应：`200 {code:0, message:"ok", data:{task_id:101, status:"APPROVED", product_status:"CANDIDATE"}}`。
- 错误：`409 E2002 状态冲突`、`403 E1003 越权`。

**创建采集任务**

- 请求：`POST /api/v1/crawl-tasks`，体 `{platform:"seller_sprite", category:"家居", page:1}`。
- 响应：`202 {code:0, data:{task_id:501, status:"PENDING"}}`。
- 错误：`503 E3001 合规开关关闭`、`429 E3002 限流`。

### 7.3 分页排序过滤、幂等限流超时

- 分页：`page`（≥1）、`page_size`（≤100）；排序 `sort=created_at:desc`；过滤 `status/pool_stage/category`。
- 幂等：写操作必带 `Idempotency-Key`，同键同请求返回同一结果或进行中；同键不同请求拒绝（BR-019）。
- 限流：接口 429；模型/采集降级（BR-021）；超时：同步 30s、异步任务 10min（待确认）。

---

## 8. 关键业务逻辑伪代码

### 8.1 选品筛选规则组合（BR-004）

```
function evaluateSelection(product, ruleVersion):
    if product.cost is null or product.price is null: return PENDING_DATA
    if ruleVersion is null or ruleVersion.status != PUBLISHED: return PENDING_CONFIG
    if not allInputsAvailable(product, ruleVersion.formula, ruleVersion.fx_config): return PENDING_DATA
    profit = calcProfit(product, ruleVersion)  # 读取货源及费用快照；含汇率快照
    monthlySales = calculateConfiguredMonthlySales(product, ruleVersion)  # A-14 口径未确认时返回待配置，不假设字段可得
    passSingle = profit >= ruleVersion.thresholds.single_profit_threshold
    passMonthly = monthlySales >= ruleVersion.thresholds.monthly_sales_threshold
    return PASS if (passSingle or passMonthly) else REJECT
    # 记录 ruleVersion、inputs、result 到 profit_calculations
```

### 8.2 利润测算（BR-003、BR-028，前端可配置）

```
function calcProfit(product, ruleVersion):
    formula = ruleVersion.formula  # 运营可编辑：成本口径/费用项
    fx = ruleVersion.fx_config     # 运营可编辑：币种/汇率值/来源/时点
    gross = safeFormulaInterpreter(formula, inputs)  # 仅允许白名单字段/算子；禁止 eval、网络和文件访问
    profit = convert_by_currency(gross, fx)  # 假设：转换方向和费用币种由配置明确；不对已换算金额重复转换
    # 记录 formula_version、fx_snapshot、inputs、result 到 profit_calculations
    return profit
```

### 8.3 侵权拦截（BR-007，专利+商标双维度）

```
function checkInfringement(product):
    patent = patentService.check(title, brand, images)
    trademark = trademarkService.check(title, brand, images)
    if patent in [INFRINGING, SUSPECTED] or trademark in [INFRINGING, SUSPECTED]: overall = BLOCK
    else if patent == PASS and trademark == PASS: overall = PASS
    else: overall = UNKNOWN  # 缺失/超时/未知：禁止入池并转人工
    save infringement_checks(product_id, patent, trademark, overall, evidence)
    if overall != PASS: block pool display
```

### 8.4 池流转（BR-009）

```
function approveReview(task):
    assert task.status == PENDING and task.reviewer has permission
    with transaction:
        lock task and product; assert expected task/product status and tenant
        update task -> APPROVED
        if task.stage == FIRST: product.pool_stage = CANDIDATE; product.status = CANDIDATE
        else: product.status = CONTENT_GEN_PENDING; create content_job
        audit(task, before, after)  # 同事务，失败则整体回滚
```

### 8.5 审核逻辑版本化（BR-011、BR-012）

```
function publishAuditRule(rule):
    with transaction:
        lock rule family and validate safe checks
        newVersion = max(version)+1
        old = getPublished(); old.status = SUPERSEDED
        rule.version = newVersion; rule.status = PUBLISHED
        audit(rule)  # 同事务，失败回滚
function rollbackAuditRule(ruleId):
    target = getVersion(ruleId); publish copy as new version
```

### 8.6 幂等与并发（BR-019、BR-020）

```
function idempotent(key, fn):
    with transaction:
        atomically insert (tenant, scope, key, request_hash) with unique constraint
        if existing: reject different hash; otherwise return stored result or in-progress status
        result = fn()  # 数据库内业务变更与幂等结果同事务；异常整体回滚
        store result; commit
    # 外部调用使用事务发件箱与下游幂等键；不承诺外部恰好一次
function transition(product, expectedStatus, nextStatus):
    update products set status=nextStatus where id=? and status=expectedStatus
    if affected==0: throw E2002 状态冲突
```

---

## 9. 前端详细设计

### 9.1 页面/路由

| 路由 | 页面 | 说明 |
|---|---|---|
| /pool | 商品池 | 列表/详情/初核 |
| /candidates | 候选池 | 复核 |
| /selection-rules | 筛选条件配置页 | 利润公式/汇率/阈值/币种/周期编辑、版本、回滚 |
| /audit-rules | 审核逻辑编辑页 | 检查项编辑、版本、回滚 |
| /content-jobs | 内容任务 | 状态/Token/结果 |
| /content-reviews | 内容审核 | 终审 |
| /listing-jobs | 上架任务 | 状态/回执 |
| /crawl-tasks | 采集任务 | 状态/失败队列 |
| /audit-logs | 审计日志 | 只读 |

### 9.2 组件、状态、API 层

- 组件：列表/详情/表单/状态徽章/版本对比。
- Pinia：`productStore`、`ruleStore`、`reviewStore`、`contentStore`。
- API 层：Axios 封装，统一鉴权头、错误拦截、幂等键生成。
- 表单校验：阈值非负、币种/汇率必填、公式语法校验、版本冲突提示。
- 权限：路由守卫 + 按钮级隐藏；越权提示。
- 状态：加载骨架、空状态、错误提示、重试。

---

## 10. 非功能设计

| 维度 | 设计 |
|---|---|
| 性能 | 分页、异步批量、索引、模型并发上限 |
| 可用性 | 健康检查、失败队列、降级、备份 |
| 缓存 | 规则/公式/汇率配置缓存（TTL 待确认） |
| 限流/超时/重试 | 三级限流、指数退避、超时 |
| 日志监控告警审计 | 结构化日志、指标、追踪、告警、审计 |
| 安全 | 鉴权、RBAC、租户隔离、脱敏、CSRF/XSS/SQL 注入防护、敏感信息加密（待确认） |

---

## 11. 异常与错误处理设计

- 统一结构：`{code, message, data}`；错误码见附录 D。
- 前端：按错误码展示（越权、冲突、限流、合规关闭等）。
- 后端：日志含 trace_id、租户、actor、入参摘要（脱敏）。

---

## 12. 测试设计要点

- 单元：规则组合、利润测算、状态机守卫。
- 接口：契约、幂等、越权、租户隔离、限流。
- 集成：采集→池→核验→生成→审核→上架全链路。
- 前端组件：表单校验、权限、加载空状态。
- 业务验收：BR 全覆盖（见测试用例文档）。

---

## 13. 部署与配置说明

- 环境变量：`DATABASE_URL`、`LLM_PROVIDER/LLM_MODEL/LLM_API_KEY/LLM_BASE_URL/LLM_QUOTA/LLM_TIMEOUT`（模型服务预留配置 A-09）、`CRAWL_ENABLED`（合规开关）、`CRAWL_PUBLIC_ONLY=true`（仅公开数据）等；汇率由前端配置（BR-028），不依赖外部汇率服务。
- 启动：Docker Compose（DEV）、Nginx（PROD）、Alembic 迁移。
- 拓扑：见概要设计第 9 章。

---

## 14. 假设与待确认项

见本章下方统一核验计划；A-01 合规、A-04 具体公式汇率、A-05 数据源和判定口径、A-09 具体供应商与能力仍待确认。


### 假设/待确认：保守默认与验证计划

| 待确认项 | 保守默认（设计假设，非已确认规则） | 验证方与冻结前行动 |
|---|---|---|
| A-01/A-02 平台条款、robots、反爬、验证码、账号风控和数据合规 | 仅公开数据；采集默认关闭，不绕过登录或验证码 | 法务与技术审查条款/robots、数据类别与频率，审批后逐源启用 |
| A-03/A-13 公开字段、1688匹配和置信阈值 | 缺字段或置信度不可用不通过，转人工 | 业务与技术核验样本、标注数据和阈值 |
| A-04/A-14 公式、费用、货币、汇率及月销售额口径 | 不预置有效值，未发布完整规则不测算；Decimal、币种与 UTC 快照 | 财务/业务提供公式、汇率方向、精度、四舍五入和期间，验算样例 |
| A-05 专利与商标来源、覆盖和判断 | 两维均有有效结果才可通过；未知/失败拦截，不给合法性保证 | 法务确认数据源、地区/时间覆盖和审核口径 |
| A-06/A-07 审核角色、SLA、发布及回退权限 | 驳回停止后续流转；保留审计，权限按最小化配置 | 业务冻结角色、SLA、驳回与发布审批流程 |
| A-08 上架方式 | 仅任务及人工处理记录，不调用未知 API，不以模拟回执证明真实上架 | 业务确认真实方式、账号与凭证和可验证回执 |
| A-09/A-11 模型、工具与存储 | 仅预留配置；模型无可信置信度时转人工；密钥不入日志 | 技术/财务核对服务契约、配额、成本和验证样本 |
| A-10/A-12 隔离及环境 | 租户字段强制隔离，环境独立；容量和部署资源不预设 | 架构/运维验证隔离、资源、备份恢复与发布流程 |

---

## 15. 附录

### 附录 A 图文件清单（导出图均未生成）

| 图 | 源文件 | 导出图 |
|---|---|---|
| 用例图（选品） | docs/attachments/usecase-selection.mmd | 待导出 |
| 用例图（内容） | docs/attachments/usecase-content.mmd | 待导出 |
| 时序图（选品） | docs/attachments/sequence-selection.mmd | 待导出 |
| 时序图（内容） | docs/attachments/sequence-content.mmd | 待导出 |
| 类图（选品） | docs/attachments/class-selection.mmd | 待导出 |
| 类图（内容） | docs/attachments/class-content.mmd | 待导出 |
| 状态图（商品） | docs/attachments/state-product.mmd | 待导出 |
| 状态图（内容） | docs/attachments/state-content.mmd | 待导出 |
| 状态图（上架） | docs/attachments/state-listing.mmd | 待导出 |

### 附录 B 接口清单

见第 7.1 节。

### 附录 C 数据表清单

见第 6.1 节。

### 附录 D 错误码清单

| 错误码 | 含义 | HTTP |
|---|---|---|
| E1001 未登录 | 鉴权失败 | 401 |
| E1003 越权 | 权限不足 | 403 |
| E2002 状态冲突 | 并发/状态不符 | 409 |
| E2004 参数错误 | 校验失败 | 422 |
| E3001 合规开关关闭 | 采集禁止 | 503 |
| E3002 限流 | 触发限流 | 429 |
| E4001 模型超时 | 模型服务超时 | 504 |
| E4002 工具调用失败 | Agent 工具失败 | 502 |

### 附录 E 术语表

见第 1.3 节。
