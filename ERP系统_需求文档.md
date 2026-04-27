# ERP系统基础框架 - 需求文档

> 版本：v1.0  
> 创建时间：2026-03-19  
> 更新记录：2026-03-19 新增测试用例文档链接

---

## 📚 文档清单

| 文档名称 | 文件路径 | 说明 |
|---------|---------|------|
| **需求文档** | `ERP系统_需求文档.md` | 本文档，包含功能需求和非功能需求 |
| **开发文档(Node)** | `ERP系统_开发文档_Node.md` | Node.js后端开发指南 |
| **开发文档(Java)** | `ERP系统_开发文档_Java.md` | Java后端开发指南 |
| **前端开发文档** | `ERP系统_开发文档_前端.md` | Vue前端开发指南 |
| **测试用例** | `ERP系统_测试用例.md` | 完整测试用例集（251个用例） |
| **接口文档** | `ERP系统_接口文档.md` | API接口定义（待补充） |

---

## 一、项目概述

### 1.1 项目背景
开发一套企业级ERP系统基础框架，提供通用的基础功能模块，支持后续业务快速扩展。

### 1.2 项目目标
- 提供完善的用户权限管理体系
- 支持可配置化的审批流程
- 实现文件分片上传和消息实时推送
- 支持单点登录和多端适配

### 1.3 技术栈
- **前端**：Vue 3 + Element Plus + TypeScript
- **后端(Node)**：NestJS + TypeORM + PostgreSQL/MySQL
- **后端(Java)**：Spring Boot + MyBatis Plus + PostgreSQL/MySQL
- **缓存**：Redis
- **消息队列**：RabbitMQ / Kafka
- **文件存储**：MinIO / 阿里云OSS
- **实时通信**：WebSocket

---

## 二、功能需求

### 2.1 菜单管理
**功能描述**：管理系统功能菜单，支持多级菜单结构

**核心功能**：
- 菜单的增删改查
- 支持目录、菜单、按钮三种类型
- 菜单排序和层级调整
- 权限标识绑定
- 菜单状态控制（启用/禁用）

**验收标准**：
- 支持无限级菜单层级
- 菜单变更实时生效
- 支持拖拽排序

### 2.2 用户管理
**功能描述**：系统用户生命周期管理

**核心功能**：
- 用户增删改查
- 批量导入/导出
- 用户状态管理（启用/禁用）
- 密码重置
- 角色分配

**验收标准**：
- 支持Excel批量导入
- 密码加密存储
- 删除用户软删除保留数据

### 2.3 角色权限管理
**功能描述**：基于RBAC的权限控制

**核心功能**：
- 角色增删改查
- 菜单权限分配
- 按钮权限分配
- 数据权限控制
- 超级管理员角色

**验收标准**：
- 权限变更实时生效
- 支持数据范围权限
- 权限缓存刷新机制

### 2.4 字典管理
**功能描述**：系统常用数据字典维护

**核心功能**：
- 字典类型管理
- 字典数据管理
- 字典缓存
- 级联字典
- 系统内置字典保护

**验收标准**：
- 字典变更自动刷新缓存
- 支持前端下拉框组件
- 支持级联选择

### 2.5 文件上传
**功能描述**：文件上传和管理

**核心功能**：
- 单文件上传
- 多文件批量上传
- 大文件分片上传
- 断点续传
- 图片/PDF预览

**验收标准**：
- 支持100MB+大文件
- 断网自动重连续传
- 文件类型和大小限制

### 2.6 消息通知
**功能描述**：系统消息和实时通知

**核心功能**：
- WebSocket实时推送
- 系统公告
- 个人消息
- 消息已读回执
- 多渠道推送（短信/邮件/钉钉）

**验收标准**：
- 消息延迟<100ms
- 支持离线消息存储
- 多端消息同步

### 2.7 单点登录
**功能描述**：统一认证和单点登录

**核心功能**：
- 用户名密码登录
- Token管理（Access/Refresh）
- 同域/跨域SSO
- 多端登录管理
- 第三方登录（OAuth/LDAP）

**验收标准**：
- Token自动刷新
- 登出全局生效
- 密码加密传输

### 2.8 审批流程
**功能描述**：可配置化审批流程引擎

**核心功能**：
- 可视化流程设计器
- 流程版本管理
- 流程实例管理
- 审批操作（通过/驳回/转交/加签）
- 流程监控和干预

**验收标准**：
- 支持条件分支
- 支持会签/或签
- 流程图实时展示进度

---

## 三、非功能需求

### 3.1 性能需求
| 指标 | 要求 |
|------|------|
| 页面加载时间 | < 2s |
| API响应时间 | 平均<200ms，95%<500ms |
| 并发用户数 | 支持1000+并发 |
| 文件上传速度 | >10MB/s |

### 3.2 安全需求
- 密码RSA加密传输
- JWT Token认证
- SQL注入/XSS防护
- 权限控制（菜单/按钮/数据）
- 操作日志记录

### 3.3 兼容性需求
- Chrome/Firefox/Safari/Edge 最新2个版本
- IE11 核心功能兼容
- 移动端响应式适配

### 3.4 可用性需求
- 系统可用性 > 99.9%
- 支持水平扩展
- 数据库读写分离

---

## 四、接口概览

### 4.1 菜单管理接口
```
POST   /api/menu              创建菜单
PUT    /api/menu/{id}         更新菜单
DELETE /api/menu/{id}         删除菜单
GET    /api/menu/{id}         查询菜单详情
GET    /api/menu/tree         获取菜单树
GET    /api/menu/list         菜单列表查询
```

### 4.2 用户管理接口
```
POST   /api/user              创建用户
PUT    /api/user/{id}         更新用户
DELETE /api/user/{id}         删除用户
GET    /api/user/{id}         查询用户详情
GET    /api/user/list         用户列表查询
POST   /api/user/import       批量导入
GET    /api/user/export       批量导出
POST   /api/user/{id}/reset-password  重置密码
```

### 4.3 角色权限接口
```
POST   /api/role              创建角色
PUT    /api/role/{id}         更新角色
DELETE /api/role/{id}         删除角色
GET    /api/role/{id}         查询角色详情
GET    /api/role/list         角色列表
PUT    /api/role/{id}/permission  分配权限
GET    /api/permission/tree   权限树
```

### 4.4 字典管理接口
```
POST   /api/dict/type         创建字典类型
PUT    /api/dict/type/{id}    更新字典类型
DELETE /api/dict/type/{id}    删除字典类型
GET    /api/dict/type/list    字典类型列表
POST   /api/dict/data         创建字典数据
PUT    /api/dict/data/{id}    更新字典数据
GET    /api/dict/data/list    字典数据列表
GET    /api/dict/{type}/data  根据类型获取字典
```

### 4.5 文件上传接口
```
POST   /api/file/upload       单文件上传
POST   /api/file/chunk        分片上传
POST   /api/file/merge        分片合并
GET    /api/file/{id}         获取文件
DELETE /api/file/{id}         删除文件
GET    /api/file/list         文件列表
```

### 4.6 消息通知接口
```
WebSocket /ws/notification     WebSocket连接
POST   /api/message/send       发送消息
GET    /api/message/list       消息列表
PUT    /api/message/{id}/read  标记已读
DELETE /api/message/{id}       删除消息
GET    /api/message/unread-count 未读消息数
```

### 4.7 单点登录接口
```
POST   /api/auth/login         登录
POST   /api/auth/logout        登出
POST   /api/auth/refresh       刷新Token
GET    /api/auth/info          获取用户信息
POST   /api/auth/sso/login     SSO登录
POST   /api/auth/sso/logout    SSO登出
```

### 4.8 审批流程接口
```
POST   /api/process/model      创建流程模型
PUT    /api/process/model/{id} 更新流程模型
POST   /api/process/model/{id}/deploy 发布流程
POST   /api/process/instance   发起流程
POST   /api/process/task/{id}/complete 审批通过
POST   /api/process/task/{id}/reject   审批驳回
POST   /api/process/task/{id}/transfer 转交
GET    /api/process/task/todo  待办任务
GET    /api/process/task/done  已办任务
GET    /api/process/instance/my 我发起的流程
```

---

## 五、数据库设计概览

### 5.1 核心表结构
```sql
-- 用户表
sys_user (id, username, password, real_name, phone, email, status, ...)

-- 角色表
sys_role (id, role_name, role_code, status, ...)

-- 用户角色关联表
sys_user_role (user_id, role_id)

-- 菜单表
sys_menu (id, parent_id, menu_name, menu_type, path, component, permission, sort, status, ...)

-- 角色菜单关联表
sys_role_menu (role_id, menu_id)

-- 字典类型表
sys_dict_type (id, dict_name, dict_code, status, ...)

-- 字典数据表
sys_dict_data (id, dict_type_id, dict_label, dict_value, sort, status, ...)

-- 文件表
sys_file (id, file_name, file_path, file_size, file_type, ...)

-- 消息表
sys_message (id, sender_id, receiver_id, title, content, type, status, ...)

-- 流程模型表
process_model (id, model_name, model_key, model_xml, version, status, ...)

-- 流程实例表
process_instance (id, model_id, business_key, status, ...)

-- 流程任务表
process_task (id, instance_id, task_name, assignee, status, ...)
```

---

## 六、项目里程碑

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| 需求分析 | Week 1 | 需求文档 |
| 技术设计 | Week 2 | 技术方案、数据库设计 |
| 基础开发 | Week 3-4 | 用户、菜单、权限模块 |
| 核心开发 | Week 5-6 | 字典、文件、消息模块 |
| 高级功能 | Week 7-8 | SSO、审批流程 |
| 测试优化 | Week 9-10 | 测试用例执行、Bug修复 |
| 上线部署 | Week 11 | 生产环境部署 |

---

## 七、相关文档链接

- 📋 [测试用例文档](./ERP系统_测试用例.md) - 包含251个测试用例，覆盖功能、性能、安全、兼容性测试
- 💻 [Node后端开发文档](./ERP系统_开发文档_Node.md) - NestJS开发规范
- ☕ [Java后端开发文档](./ERP系统_开发文档_Java.md) - Spring Boot开发规范
- 🎨 [前端开发文档](./ERP系统_开发文档_前端.md) - Vue开发规范
- 🔌 [接口文档](./ERP系统_接口文档.md) - 详细API定义

---

*文档创建：2026-03-19*  
*最后更新：2026-03-19*  
*维护人：产品团队*
