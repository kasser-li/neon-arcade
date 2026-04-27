# ERP系统基础框架 - Node后端开发文档

> 技术栈：NestJS + TypeORM + PostgreSQL/MySQL + Redis
> 版本：v1.0  
> 创建时间：2026-03-19

---

## 📚 文档清单

| 文档名称 | 文件路径 | 说明 |
|---------|---------|------|
| **需求文档** | `ERP系统_需求文档.md` | 功能需求和非功能需求 |
| **开发文档(Node)** | `ERP系统_开发文档_Node.md` | 本文档，Node.js后端开发指南 |
| **开发文档(Java)** | `ERP系统_开发文档_Java.md` | Java后端开发指南 |
| **前端开发文档** | `ERP系统_开发文档_前端.md` | Vue前端开发指南 |
| **测试用例** | `ERP系统_测试用例.md` | 完整测试用例集（251个用例） |
| **接口文档** | `ERP系统_接口文档.md` | API接口定义 |

---

## 一、项目初始化

### 1.1 环境要求
```bash
Node.js >= 18.0.0
npm >= 9.0.0
PostgreSQL >= 14.0 或 MySQL >= 8.0
Redis >= 7.0
```

### 1.2 创建项目
```bash
# 安装NestJS CLI
npm i -g @nestjs/cli

# 创建项目
nest new erp-system-backend

# 进入项目目录
cd erp-system-backend

# 安装核心依赖
npm install @nestjs/common @nestjs/core @nestjs/platform-express
npm install @nestjs/typeorm typeorm pg  # PostgreSQL
# 或
npm install mysql2  # MySQL

# 安装其他依赖
npm install @nestjs/config @nestjs/jwt @nestjs/passport
npm install passport passport-jwt passport-local
npm install bcryptjs class-validator class-transformer
npm install @nestjs/websockets @nestjs/platform-socket.io
npm install ioredis multer @types/multer
npm install uuid @types/uuid dayjs
npm install lodash @types/lodash
npm install xlsx  # Excel处理
npm install minio  # 文件存储
```

### 1.3 项目结构
```
erp-system-backend/
├── src/
│   ├── app.module.ts              # 根模块
│   ├── main.ts                    # 入口文件
│   ├── config/                    # 配置文件
│   │   ├── database.config.ts
│   │   ├── redis.config.ts
│   │   └── jwt.config.ts
│   ├── common/                    # 公共模块
│   │   ├── decorators/            # 装饰器
│   │   ├── filters/               # 异常过滤器
│   │   ├── guards/                # 守卫
│   │   ├── interceptors/          # 拦截器
│   │   ├── pipes/                 # 管道
│   │   └── utils/                 # 工具函数
│   ├── modules/                   # 业务模块
│   │   ├── auth/                  # 认证模块
│   │   ├── user/                  # 用户模块
│   │   ├── role/                  # 角色模块
│   │   ├── menu/                  # 菜单模块
│   │   ├── dict/                  # 字典模块
│   │   ├── file/                  # 文件模块
│   │   ├── message/               # 消息模块
│   │   └── process/               # 流程模块
│   └── shared/                    # 共享模块
│       ├── services/
│       └── entities/
├── test/                          # 测试文件
├── uploads/                       # 上传文件目录
└── package.json
```

---

## 二、核心配置

### 2.1 数据库配置
```typescript
// src/config/database.config.ts
import { TypeOrmModuleOptions } from '@nestjs/typeorm';

export const databaseConfig: TypeOrmModuleOptions = {
  type: 'postgres',  // 或 'mysql'
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT) || 5432,
  username: process.env.DB_USER || 'erp_user',
  password: process.env.DB_PASSWORD || 'password',
  database: process.env.DB_NAME || 'erp_db',
  entities: [__dirname + '/../**/*.entity{.ts,.js}'],
  synchronize: process.env.NODE_ENV !== 'production',
  logging: process.env.NODE_ENV === 'development',
  poolSize: 10,
  extra: {
    max: 20,
    connectionTimeoutMillis: 2000,
  },
};
```

### 2.2 Redis配置
```typescript
// src/config/redis.config.ts
import { RedisOptions } from 'ioredis';

export const redisConfig: RedisOptions = {
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT) || 6379,
  password: process.env.REDIS_PASSWORD,
  db: parseInt(process.env.REDIS_DB) || 0,
  retryStrategy: (times) => Math.min(times * 50, 2000),
};
```

### 2.3 JWT配置
```typescript
// src/config/jwt.config.ts
export const jwtConfig = {
  secret: process.env.JWT_SECRET || 'your-secret-key',
  accessTokenExpiresIn: '2h',
  refreshTokenExpiresIn: '7d',
};
```

---

## 三、核心模块实现

### 3.1 用户模块

#### 实体定义
```typescript
// src/modules/user/entities/user.entity.ts
import { Entity, Column, PrimaryGeneratedColumn, CreateDateColumn, UpdateDateColumn } from 'typeorm';

@Entity('sys_user')
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true, length: 50 })
  username: string;

  @Column({ length: 100 })
  password: string;

  @Column({ length: 50, nullable: true })
  realName: string;

  @Column({ length: 20, nullable: true })
  phone: string;

  @Column({ length: 100, nullable: true })
  email: string;

  @Column({ default: 1 })
  status: number;  // 0-禁用 1-启用

  @Column({ default: 0 })
  isDeleted: number;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}
```

#### DTO定义
```typescript
// src/modules/user/dto/create-user.dto.ts
import { IsString, IsOptional, IsEmail, Length, Matches } from 'class-validator';

export class CreateUserDto {
  @IsString()
  @Length(2, 20)
  username: string;

  @IsString()
  @Length(2, 50)
  realName: string;

  @IsOptional()
  @IsString()
  @Matches(/^1[3-9]\d{9}$/)
  phone?: string;

  @IsOptional()
  @IsEmail()
  email?: string;

  @IsOptional()
  @IsString()
  roleIds?: string[];
}
```

#### Service实现
```typescript
// src/modules/user/user.service.ts
import { Injectable, ConflictException, NotFoundException } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcryptjs';
import { User } from './entities/user.entity';
import { CreateUserDto } from './dto/create-user.dto';

@Injectable()
export class UserService {
  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  async create(createUserDto: CreateUserDto): Promise<User> {
    // 检查用户名是否存在
    const existingUser = await this.userRepository.findOne({
      where: { username: createUserDto.username, isDeleted: 0 },
    });
    if (existingUser) {
      throw new ConflictException('用户名已存在');
    }

    // 生成默认密码
    const defaultPassword = await bcrypt.hash('123456', 10);

    const user = this.userRepository.create({
      ...createUserDto,
      password: defaultPassword,
    });

    return this.userRepository.save(user);
  }

  async findAll(query: any) {
    const { page = 1, pageSize = 10, username, status } = query;
    
    const queryBuilder = this.userRepository.createQueryBuilder('user')
      .where('user.isDeleted = :isDeleted', { isDeleted: 0 });

    if (username) {
      queryBuilder.andWhere('user.username LIKE :username', { username: `%${username}%` });
    }

    if (status !== undefined) {
      queryBuilder.andWhere('user.status = :status', { status });
    }

    const [list, total] = await queryBuilder
      .skip((page - 1) * pageSize)
      .take(pageSize)
      .getManyAndCount();

    return { list, total, page, pageSize };
  }

  async findOne(id: string): Promise<User> {
    const user = await this.userRepository.findOne({
      where: { id, isDeleted: 0 },
    });
    if (!user) {
      throw new NotFoundException('用户不存在');
    }
    return user;
  }

  async update(id: string, updateUserDto: any): Promise<User> {
    const user = await this.findOne(id);
    Object.assign(user, updateUserDto);
    return this.userRepository.save(user);
  }

  async remove(id: string): Promise<void> {
    const user = await this.findOne(id);
    user.isDeleted = 1;
    await this.userRepository.save(user);
  }

  async resetPassword(id: string): Promise<string> {
    const user = await this.findOne(id);
    const newPassword = Math.random().toString(36).slice(-8);
    user.password = await bcrypt.hash(newPassword, 10);
    await this.userRepository.save(user);
    return newPassword;
  }
}
```

#### Controller实现
```typescript
// src/modules/user/user.controller.ts
import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards } from '@nestjs/common';
import { UserService } from './user.service';
import { CreateUserDto } from './