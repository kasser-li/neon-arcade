# OpenSpec Rules 模板（初版）

> 使用说明：将以下文件放入项目的 `.openspec/rules/` 目录，根据实际技术栈调整

---

## 📁 文件结构

```
.openspec/rules/
├── 00-general.md        # 通用规范（所有角色都遵守）
├── 10-backend.md        # 后端开发规范
├── 20-frontend.md       # 前端开发规范
├── 30-database.md       # 数据库规范
├── 40-testing.md        # 测试规范
└── 50-security.md       # 安全规范
```

---

## 📄 00-general.md（通用规范）

```markdown
# 通用开发规范

## 代码风格
- 使用 4 个空格缩进，不使用 Tab
- 行宽限制 120 字符
- 命名使用驼峰式（camelCase），常量使用大写蛇形（UPPER_SNAKE）
- 所有代码必须包含中文注释，复杂逻辑需要详细说明

## 提交规范
- Commit Message 格式：`[类型] 描述 (关联 Issue)`
- 类型包括：feat, fix, docs, style, refactor, test, chore
- 示例：`[feat] 新增用户登录功能 (ISSUE-123)`

## 文档要求
- 每个公共方法必须有 JSDoc/JavaDoc 注释
- API 接口必须有完整的请求/响应示例
- 数据库变更必须有 SQL 脚本和回滚脚本

## 禁止行为
- ❌ 禁止硬编码魔法值（使用常量或配置）
- ❌ 禁止打印敏感信息（密码、Token 等）
- ❌ 禁止提交 TODO 不处理
- ❌ 禁止忽略异常（必须捕获并处理或记录日志）

## AI 生成代码要求
- 生成的代码必须可编译、可运行
- 必须遵循项目现有代码风格
- 必须包含必要的错误处理
- 必须生成对应的单元测试
```

---

## 📄 10-backend.md（后端规范）

```markdown
# 后端开发规范（Java/Spring Boot）

## 技术栈
- JDK 21（新项目）/ JDK 8（旧项目）
- Spring Boot 3.x
- MyBatis-Plus / JPA
- MySQL 8.0+
- Redis 6.x

## 分层架构
```
controller → service → mapper → entity
                    ↓
                 dto/vo
```

## Controller 层规范
- 使用 `@RestController` 注解
- 所有接口必须返回统一响应结构 `Result<T>`
- 路径使用复数名词：`/api/users`, `/api/orders`
- HTTP 方法语义化：GET(查询), POST(新增), PUT(修改), DELETE(删除)

## Service 层规范
- 使用 `@Service` 注解
- 事务注解 `@Transactional` 放在 Service 层
- 业务异常抛出自定义异常类 `BusinessException`
- 禁止在 Service 层直接操作数据库（必须通过 Mapper）

## Mapper 层规范
- 使用 MyBatis-Plus 的 `BaseMapper<T>`
- 复杂查询使用 XML 或 `@SelectProvider`
- 禁止在 Mapper 层编写业务逻辑

## 实体类规范
- 使用 Lombok 简化代码：`@Data`, `@Builder`, `@NoArgsConstructor`
- 数据库字段使用 `@TableName` 明确指定表名
- 主键使用 `@TableId(type = IdType.ASSIGN_UUID)`
- 必须包含创建时间、更新时间、逻辑删除字段

## DTO/VO 规范
- DTO（Data Transfer Object）：用于接收请求参数
- VO（View Object）：用于返回前端数据
- 禁止直接使用 Entity 作为响应对象
- 使用 `@JsonIgnore` 忽略敏感字段

## 统一响应结构
```java
@Data
public class Result<T> {
    private Integer code;    // 200 成功，其他为失败
    private String message;  // 响应消息
    private T data;          // 响应数据
    private Long timestamp;  // 时间戳
}
```

## 异常处理
- 全局异常处理器使用 `@RestControllerAdvice`
- 业务异常：`BusinessException(code, message)`
- 系统异常：记录完整堆栈日志

## 日志规范
- 使用 SLF4J + Logback
- 日志级别：ERROR(错误), WARN(警告), INFO(信息), DEBUG(调试)
- 生产环境禁止输出 DEBUG 日志
- 关键操作必须记录审计日志

## AI 生成代码要求
- 优先使用 MyBatis-Plus 的 CRUD 方法
- 批量操作使用批量接口，禁止循环调用
- 分页查询使用 `Page<T>` 对象
- SQL 注入防护：使用参数化查询，禁止字符串拼接
```

---

## 📄 20-frontend.md（前端规范）

```markdown
# 前端开发规范（Vue 3 + TypeScript）

## 技术栈
- Vue 3.x（Composition API）
- TypeScript 5.x
- Vite 5.x
- Element Plus / Ant Design Vue
- Axios
- Pinia（状态管理）

## 目录结构
```
src/
├── api/           # API 接口
├── assets/        # 静态资源
├── components/    # 公共组件
├── composables/   # 组合式函数
├── layouts/       # 布局组件
├── router/        # 路由配置
├── stores/        # Pinia 状态
├── types/         # TypeScript 类型
├── utils/         # 工具函数
├── views/         # 页面组件
└── App.vue
```

## 组件开发规范
- 使用 `.vue` 单文件组件
- 脚本使用 `<script setup lang="ts">`
- 组件命名使用 PascalCase（大驼峰）
- 文件名与组件名一致

## Props 定义
```typescript
const props = defineProps<{
  title: string
  count?: number
  loading?: boolean
}>()
```

## Emits 定义
```typescript
const emit = defineEmits<{
  (e: 'update', value: string): void
  (e: 'submit', data: FormData): void
}>()
```

## API 调用规范
- 所有 API 请求封装在 `src/api/` 目录
- 使用 Axios 拦截器统一处理请求响应
- 错误提示使用全局 Message 组件
- 禁止在组件内直接调用 `axios.get/post`

## 状态管理规范
- 使用 Pinia 管理全局状态
- 每个模块独立 store 文件
- 使用 `storeToRefs` 保持响应式

## 路由规范
- 使用 Vue Router 4.x
- 路由配置集中管理 `src/router/index.ts`
- 需要权限的页面添加路由守卫
- 路由命名使用 kebab-case（短横线）

## 样式规范
- 使用 SCSS 预处理器
- 组件样式使用 `scoped`
- 全局样式变量放在 `src/styles/variables.scss`
- 禁止使用 `!important`

## 响应式布局
- 使用 flex/grid 布局
- 移动端优先（Mobile First）
- 断点：sm(640px), md(768px), lg(1024px), xl(1280px)

## 性能优化
- 图片使用懒加载
- 路由使用懒加载：`() => import('@/views/xxx.vue')`
- 大数据列表使用虚拟滚动
- 防抖节流处理频繁操作

## AI 生成代码要求
- 优先使用 Composition API
- 类型定义完整，禁止使用 `any`
- 组件可复用，避免重复代码
- 必须处理加载状态和错误状态
```

---

## 📄 30-database.md（数据库规范）

```markdown
# 数据库开发规范

## 设计规范
- 表名使用小写蛇形：`user_info`, `order_detail`
- 字段名使用小写蛇形：`user_name`, `create_time`
- 必须包含主键（id）、创建时间、更新时间、逻辑删除
- 所有字段必须有注释

## 必填字段
```sql
id              VARCHAR(32)   PRIMARY KEY  -- 主键
create_time     DATETIME      NOT NULL     -- 创建时间
update_time     DATETIME      NOT NULL     -- 更新时间
create_by       VARCHAR(32)                -- 创建人
update_by       VARCHAR(32)                -- 更新人
deleted         TINYINT(1)    DEFAULT 0    -- 逻辑删除
```

## 索引规范
- 主键索引：`PRIMARY KEY (id)`
- 外键索引：`INDEX idx_xxx (xxx_id)`
- 查询条件字段必须添加索引
- 禁止在索引字段上使用函数或计算

## 字符集
- 字符集：`utf8mb4`
- 排序规则：`utf8mb4_general_ci`

## 数据类型选择
| 场景 | 类型 | 说明 |
|------|------|------|
| 主键 | VARCHAR(32) | 使用 UUID |
| 金额 | DECIMAL(18,2) | 禁止使用 FLOAT/DOUBLE |
| 状态 | TINYINT | 0/1 或枚举值 |
| 大文本 | TEXT | 超过 1000 字符 |
| 时间 | DATETIME | 禁止使用 TIMESTAMP |

## SQL 编写规范
- 使用参数化查询，禁止 SQL 注入
- 禁止 `SELECT *`，必须明确字段列表
- 多表关联使用 INNER JOIN，禁止隐式关联
- 分页查询必须带排序字段

## 变更管理
- 所有表结构变更必须有 SQL 脚本
- 必须提供回滚脚本
- 生产环境变更需要 DBA 审核

## AI 生成代码要求
- 生成的 SQL 必须符合上述规范
- 自动添加必填字段
- 索引命名遵循规范
- 提供完整的建表语句和注释
```

---

## 📄 40-testing.md（测试规范）

```markdown
# 测试开发规范

## 测试分类
| 类型 | 工具 | 覆盖率要求 |
|------|------|-----------|
| 单元测试 | JUnit / Vitest | 核心代码 > 80% |
| 集成测试 | SpringBootTest | 关键流程 > 90% |
| E2E 测试 | Playwright | 核心页面 > 100% |

## 单元测试规范
- 测试类命名：`XxxTest`
- 测试方法命名：`testXxx_场景_预期结果`
- 使用 AAA 模式：Arrange-Act-Assert
- 每个测试方法只验证一个场景

## 示例（Java）
```java
@Test
@DisplayName("测试用户登录_成功_返回用户信息")
void testLogin_Success_ReturnUserInfo() {
    // Arrange
    String username = "test";
    String password = "123456";
    
    // Act
    Result<UserVO> result = userService.login(username, password);
    
    // Assert
    assertEquals(200, result.getCode());
    assertNotNull(result.getData());
}
```

## 集成测试规范
- 使用 `@SpringBootTest` 启动完整容器
- 测试数据使用 `@Transactional` 自动回滚
- 禁止依赖外部服务（使用 Mock）

## Playwright 自动化测试
- 测试文件放在 `tests/e2e/` 目录
- 使用 Page Object 模式
- 测试用例输出 Excel 报告
- 核心流程必须覆盖：新增、编辑、删除、查询

## 测试数据管理
- 使用测试工厂类生成测试数据
- 禁止硬编码测试数据
- 测试数据必须可清理

## AI 生成代码要求
- 生成的代码必须包含单元测试
- 测试用例覆盖正常场景和异常场景
- Mock 外部依赖
- 提供测试数据准备和清理方法
```

---

## 📄 50-security.md（安全规范）

```markdown
# 安全开发规范

## 认证授权
- 使用 JWT Token 认证
- Token 有效期 2 小时，Refresh Token 7 天
- 接口权限使用注解 `@PreAuthorize("hasRole('ADMIN')")`
- 禁止硬编码密钥

## 数据加密
- 密码使用 BCrypt 加密
- 敏感数据传输使用 HTTPS
- 数据库敏感字段加密存储

## 输入验证
- 所有用户输入必须验证
- 使用 JSR-303 验证注解：`@NotNull`, `@Size`, `@Pattern`
- 文件上传限制类型和大小

## XSS 防护
- 前端输出使用转义
- 后端使用 HTML 过滤器
- 禁止直接渲染用户输入

## CSRF 防护
- 开启 CSRF Token
- 敏感操作使用 POST 请求
- 验证 Referer 头

## SQL 注入防护
- 使用参数化查询
- 禁止字符串拼接 SQL
- 使用 ORM 框架

## 日志安全
- 禁止记录敏感信息（密码、身份证号、银行卡号）
- 日志文件设置访问权限
- 定期清理日志

## AI 生成代码要求
- 生成的代码必须通过安全扫描
- 禁止生成有安全漏洞的代码
- 敏感操作必须添加权限验证
- 所有接口必须有输入验证
```

---

## 🔧 使用方式

### 1. 项目初始化

```bash
# 在项目根目录执行
openspec init

# 将 rules 模板复制到 .openspec/rules/ 目录
cp -r rules-template/* .openspec/rules/
```

### 2. 自定义调整

根据项目实际情况调整：
- 技术栈版本
- 代码风格偏好
- 业务流程特殊要求
- 团队规范

### 3. 持续优化

每次开发后执行：
```
提示词："在这次开发中发现了以下问题：[具体问题]
       请根据这些问题优化 rules 文件"
```

---

## 📌 注意事项

1. **Rules 文件控制在 200 行以内** - AI 遵循效果最好
2. **规则不要冲突** - 避免 AI 困惑
3. **定期 Review** - 随着项目发展更新规范
4. **团队共识** - 所有成员遵守同一套规范

---

*版本：v1.0 | 创建时间：2026-04-15 | 基于《CUC-总部区-SDD 实践经验》整理*
