# 智能实验室预约系统

基于 **FastAPI + Vue 3 + LangGraph** 的实验室预约管理系统。

项目除了常规的实验室 / 设备 / 预约管理之外，内置了一个**能查询真实数据库、并在用户确认后真正落库下单的 AI Agent** —— 用自然语言即可完成「查实验室 → 查设备 → 确认信息 → 提交预约」的完整流程。

---

## 功能特性

### 基础业务

- 用户注册 / 登录，基于 JWT 的无状态鉴权，角色分为 `student` 与 `admin`
- 实验室管理：封面、位置、容量、每日开放时间段、启用状态
- 实验室设备管理：型号规格、数量、维修状态，设备挂在实验室之下
- 预约管理：同一张表同时支持「预约整个实验室」与「预约某台设备」
- 时段冲突检测：基于区间重叠判断，避免同一时段被重复预约
- 管理员审核闭环：提交后为待审核，管理员通过 / 拒绝后才可实际使用
- 过期预约自动回收：后台定时任务把过期仍未审核的预约置为已取消
- 文件上传：后缀白名单、大小上限、流式落盘与唯一文件名

### AI Agent

- 基于 LangGraph 的 `StateGraph` + `ToolNode` 工具调用循环
- 6 个工具：知识库检索、开放实验室查询、实验室设备查询、创建预约、取消预约、获取当天日期
- RAG 知识库：预约规则 / 开放时间 / 设备使用 / 安全规范四篇文档，Chroma 向量检索
- SSE 流式输出：前端逐字打字机效果，并实时展示「正在检索实验室知识库…」等过程文案
- 防呆约束：日期先查询不反问用户、落库前必须复述信息并等待用户明确确认、禁止编造库中不存在的数据

---

## 技术栈

| 层次       | 技术                                                          |
| ---------- | ------------------------------------------------------------- |
| 后端框架   | FastAPI 0.115                                                 |
| ORM / 数据库 | SQLAlchemy 2.0 + PyMySQL（MySQL）                            |
| 鉴权       | PyJWT + bcrypt                                                |
| AI 编排    | LangGraph 1.2 + langchain-openai                              |
| 向量检索   | ChromaDB + sentence-transformers（`BAAI/bge-small-zh-v1.5`）  |
| 前端框架   | Vue 3 + Vite                                                  |
| UI 组件库  | Element Plus                                                  |
| 路由 / 请求 | vue-router + axios                                           |
| Markdown   | marked + DOMPurify（解析并过滤，防 XSS）                       |

前端要求 Node.js `^22.18.0 || >=24.12.0`。

---

## 目录结构

```
lab agent system/
├── .vscode/
│   └── launch.json              # debugpy 调试配置（uvicorn 启动 app.main:app）
├── backend/
│   ├── app/
│   │   ├── api/                 # 路由层：只负责接收参数、调用 service、包装响应
│   │   │   ├── __init__.py      # 汇总各路由，统一挂载 /api 前缀
│   │   │   ├── auth.py          # 登录 / 注册
│   │   │   ├── user.py          # 个人信息与用户管理
│   │   │   ├── lab.py           # 实验室管理
│   │   │   ├── equipment.py     # 设备管理
│   │   │   ├── reservation.py   # 预约与审核
│   │   │   ├── files.py         # 文件上传
│   │   │   └── ai.py            # AI 对话（普通返回 + SSE 流式）
│   │   ├── common/              # 统一响应格式与全局异常处理
│   │   ├── dependencies/        # 当前登录用户 / 管理员依赖
│   │   ├── models/              # SQLAlchemy 数据模型
│   │   ├── schemas/             # Pydantic 出入参
│   │   ├── services/            # 业务逻辑层
│   │   ├── utils/               # JWT 与密码工具
│   │   ├── config.py            # 配置项与常量
│   │   ├── database.py          # 引擎、会话、Base
│   │   └── main.py              # 应用入口
│   ├── data/
│   │   ├── kb/                  # 知识库源文件（Markdown）
│   │   └── chroma/              # 向量库持久化目录
│   ├── uploads/                 # 上传文件存储目录
│   ├── .env                     # 环境变量（需自行创建）
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/                 # 接口封装
    │   ├── assets/              # 样式与图片
    │   ├── components/          # 公共组件
    │   ├── layouts/             # 主框架布局
    │   ├── router/              # 路由表与登录守卫
    │   ├── utils/               # axios 实例、token 存取
    │   └── views/               # 页面
    ├── vite.config.js           # 路径别名与接口代理
    └── package.json
```

---

## 快速开始

### 1. 准备数据库

先创建一个空库，例如 `smart_lab`，字符集建议 `utf8mb4`。表结构由程序在首次启动时自动创建，无需手工建表。

### 2. 启动后端

```bash
cd backend

# 建议使用虚拟环境
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

首次启动会加载向量模型并预热知识库，日志出现相关提示后再发请求，可避免第一个请求超时。

> 注意：`backend/.env` 需要自行创建，缺少必填配置时程序会在启动阶段直接报错。

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 <http://localhost:5173>，后端接口文档在 <http://127.0.0.1:8000/docs>。

### 4. 使用 VS Code 调试

项目已内置调试配置，打开 `backend` 目录后直接运行 `Python Debugger: FastAPI` 即可，等同于手动执行 `uvicorn app.main:app`。

---

## 环境变量

在 `backend/.env` 中配置，由 `pydantic-settings` 读取：

| 变量名             | 必填 | 默认值   | 说明                                                     |
| ------------------ | ---- | -------- | -------------------------------------------------------- |
| `DATABASE_URL`     | 是   | —        | MySQL 连接串，如 `mysql+pymysql://用户:密码@127.0.0.1:3306/smart_lab?charset=utf8mb4` |
| `JWT_SECRET_KEY`   | 是   | —        | JWT 签名密钥，请使用足够随机的长字符串                   |
| `JWT_EXPIRE_HOURS` | 否   | `24`     | Token 有效期（小时）                                     |
| `JWT_ALGORITHM`    | 否   | `HS256`  | JWT 签名算法                                             |
| `LLM_API_KEY`      | 是   | —        | 大模型 API Key                                           |
| `LLM_BASE_URL`     | 是   | —        | 兼容 OpenAI 协议的接口地址                               |
| `LLM_MODEL`        | 是   | —        | 模型名称                                                 |

---

## 数据模型

| 表名           | 说明       | 关键字段                                                                                     |
| -------------- | ---------- | -------------------------------------------------------------------------------------------- |
| `users`        | 用户信息   | `username`（唯一）、`password`（bcrypt 密文）、`role`、`name`、`email`、`phone`、`avatar`、`status` |
| `labs`         | 实验室信息 | `name`、`description`、`img`、`location`、`capacity`、`open_time`、`close_time`、`status`      |
| `equipments`   | 实验室设备 | `lab_id`（外键）、`name`、`spec`、`quantity`、`img`、`status`（0 维修 / 1 正常）                |
| `reservations` | 预约信息   | `user_id`、`lab_id`、`equipment_id`、`date`、`start_time`、`end_time`、`remark`、`status`      |

所有表都继承自 `Base`，自动带有 `id`、`create_time`、`update_time` 三个公共字段。

几处值得注意的设计：

- **`reservations.equipment_id` 为空表示预约整个实验室，非空表示预约具体设备**，用同一张表承载两种预约。
- `reservations.status`：`0` 待审核、`1` 已通过、`2` 已拒绝、`3` 已取消。
- `date` 与 `start_time` / `end_time` 均以字符串存储（如 `2026-09-27` 与 `09:00`），因此可以直接做字符串比较来校验先后顺序。
- 登录校验要求 `users.status == 1`。

---

## 接口一览

所有接口统一挂载在 `/api` 前缀下，返回值统一为 `{ code, message, data }` 结构（业务错误码放在 `code` 字段中，HTTP 状态码可能仍为 200）。

### 权限验证

| 方法 | 路径                 | 说明           | 权限 |
| ---- | -------------------- | -------------- | ---- |
| POST | `/api/auth/login`    | 登录，返回 JWT | 公开 |
| POST | `/api/auth/register` | 注册           | 公开 |

### 用户

| 方法   | 路径                    | 说明               | 权限     |
| ------ | ----------------------- | ------------------ | -------- |
| GET    | `/api/user/me`          | 获取当前用户信息   | 登录用户 |
| PUT    | `/api/user/me`          | 修改当前用户信息   | 登录用户 |
| PUT    | `/api/user/password`    | 修改当前用户密码   | 登录用户 |
| GET    | `/api/user/list`        | 分页查询用户       | 管理员   |
| POST   | `/api/user`             | 新增用户           | 管理员   |
| PUT    | `/api/user/{user_id}`   | 修改指定用户       | 管理员   |
| DELETE | `/api/user/{user_id}`   | 删除指定用户       | 管理员   |

### 实验室与设备

| 方法   | 路径                            | 说明             | 权限     |
| ------ | ------------------------------- | ---------------- | -------- |
| GET    | `/api/lab/list`                 | 分页查询实验室   | 登录用户 |
| GET    | `/api/lab/{lab_id}`             | 查询实验室详情   | 登录用户 |
| POST   | `/api/lab`                      | 新增实验室       | 管理员   |
| PUT    | `/api/lab/{lab_id}`             | 修改实验室       | 管理员   |
| DELETE | `/api/lab/{lab_id}`             | 删除实验室       | 管理员   |
| GET    | `/api/equipment/list`           | 分页查询设备     | 登录用户 |
| POST   | `/api/equipment`                | 新增设备         | 管理员   |
| PUT    | `/api/equipment/{equipment_id}` | 修改设备         | 管理员   |
| DELETE | `/api/equipment/{equipment_id}` | 删除设备         | 管理员   |

### 预约

| 方法 | 路径                                | 说明                       | 权限     |
| ---- | ----------------------------------- | -------------------------- | -------- |
| GET  | `/api/reservation/list`             | 分页查询预约（管理员可见全部，学生仅见自己的） | 登录用户 |
| POST | `/api/reservation`                  | 提交预约                   | 登录用户 |
| PUT  | `/api/reservation/{id}/cancel`      | 取消自己的预约             | 登录用户 |
| PUT  | `/api/reservation/{id}/audit`       | 审核预约（通过 / 拒绝）    | 管理员   |

### 文件与 AI

| 方法 | 路径                    | 说明                       | 权限     |
| ---- | ----------------------- | -------------------------- | -------- |
| POST | `/api/files/upload`     | 上传文件，返回可访问 URL   | 登录用户 |
| POST | `/api/ai/chat`          | AI 对话，一次性返回        | 登录用户 |
| POST | `/api/ai/chat/stream`   | AI 对话，SSE 流式返回      | 登录用户 |

上传的静态文件通过 `/uploads/{文件名}` 直接访问。

---

## 预约校验规则

提交预约时会依次校验，任一不通过则返回业务错误：

1. 预约日期不能早于当天
2. 结束时间不能早于开始时间
3. 当天预约时，开始时间不能早于当前时间
4. 实验室必须存在且处于开放状态
5. 预约时段必须落在实验室的开放时间段内
6. 若预约设备，设备必须存在且不处于维修状态
7. 时段冲突检测：同一天、同一实验室（或同一设备）、状态为待审核或已通过的记录中，不允许存在时间区间重叠

冲突判断使用区间重叠而非逐时段比对：

```
已有预约.start_time < 本次.end_time  且
已有预约.end_time   > 本次.start_time
```

此外，预约整个实验室与预约设备是两条互不干扰的线：预约实验室时只与「实验室级预约」比较，预约设备时只与「同一设备的预约」比较。

---

## AI Agent 设计

### 整体流程

```
用户提问 → 组装 SystemPrompt + 历史消息 → LangGraph 图
        → agent 节点调用大模型
        → 若产生 tool_call → ToolNode 执行工具 → 结果回灌给 agent 节点
        → 无 tool_call → 输出最终回答
```

图的节点与边定义在 `backend/app/services/agent_service.py`，递归上限设为 10，防止 agent 与工具之间空转。

### 工具列表

| 工具名                  | 作用                             |
| ----------------------- | -------------------------------- |
| `search_lab_docs`       | 检索实验室知识库（RAG）          |
| `list_open_labs`        | 查询开放中的实验室               |
| `list_lab_equipments`   | 查询指定实验室下的设备           |
| `create_lab_reservation`| 创建预约并写入数据库             |
| `cancle_reservation`    | 取消已有的预约                   |
| `get_today`             | 获取服务器当前日期               |

工具全部使用 `@tool` 装饰器定义，内部用 `try / except` 把异常转换成 `{"ok": false, "error": "..."}` 返回给模型，保证工具不会打断整张图。

### 提示词约束

系统提示词中设置了若干硬性约束，用于抑制幻觉与误操作：

- 涉及「今天 / 明天 / 后天」等相对日期时，必须先调用 `get_today`，不允许直接反问用户
- 提交预约前必须向用户复述实验室（或设备）的 ID 与名称、日期、开始与结束时间，并等待用户明确确认
- 用户未明确回复「确认」之前，不得调用 `create_lab_reservation`
- 缺少 `lab_id` / `equipment_id` 时必须先查询获得，不允许凭空编造
- 规则、开放时间类问题优先检索知识库，不凭空回答

### 流式输出协议

`/api/ai/chat/stream` 使用 SSE，每帧形如 `data: {json}\n\n`，事件类型如下：

| `type`       | 含义                     | 主要字段              |
| ------------ | ------------------------ | --------------------- |
| `status`     | 状态提示                 | `message`             |
| `tool_start` | 开始调用某个工具         | `name`、`label`       |
| `tool_end`   | 工具调用结束             | `name`、`label`、`preview` |
| `token`      | 模型输出的增量文本       | `content`             |
| `done`       | 正常结束                 | —                     |
| `error`      | 出错（流已开始，只能以事件形式返回） | `message` |

前端使用 `fetch` + `ReadableStream` 读取（而非 `EventSource`，因为需要携带自定义鉴权头），按 `\n\n` 切分帧并对不完整的半包做缓冲。

### 知识库与检索

- 知识库源文件位于 `backend/data/kb/`，当前包含预约规则、开放时间、设备使用、安全规范四篇 Markdown
- 文档以「整篇文件」为粒度入库，向量库 ID 即文件名
- 嵌入模型为 `BAAI/bge-small-zh-v1.5`，采用懒加载单例，避免重复加载
- 检索时会取相似度最高的若干条，按 `1 / (1 + 距离)` 归一化打分，丢弃分数低于 `0.5` 的结果，最终最多取前 2 篇拼入提示词
- 应用启动阶段会预热向量模型，把首次加载开销前置，避免首个用户请求超时

---

## 说明

- 后端所有接口的返回值都经过 `Response` 统一包装，前端在响应拦截器中依据 `data.code` 判断成功与否，遇到 `401` 会自动清除本地登录状态并跳转登录页。
- 数据库表结构由 `Base.metadata.create_all()` 在应用启动时创建，项目暂未引入 Alembic 迁移。生产环境建议改用迁移工具管理表结构变更。
