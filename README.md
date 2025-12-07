# README

## 目录结构

```text
llmops-api/
    ├── app/               # 应用入口集合
    │   └── http/          # HTTP 服务入口
    ├── config/            # 应用配置文件
    ├── internal/          # 应用内部逻辑
    │   ├── core/          # LLM 核心代码
    │   ├── exception/     # 异常定义
    │   ├── extension/     # Flask 扩展
    │   ├── handler/       # 路由处理器 / 控制器
    │   ├── middleware/    # 中间件 (鉴权 / 校验等)
    │   ├── migration/     # 数据库迁移文件
    │   ├── model/         # 数据库模型
    │   ├── router/        # 路由定义 / 注册
    │   ├── schedule/      # 定时 / 调度任务
    │   ├── schema/        # 请求 / 响应结构体
    │   ├── server/        # 服务启动 / 构建相关
    │   ├── service/       # 服务层逻辑
    │   └── task/          # 异步 / 延迟任务
    ├── pkg/               # 扩展包 / 第三方集成
    ├── storage/           # 本地存储 (文件 / 上传 /缓存等)
    ├── test/              # 测试代码
    ├── venv/              # 虚拟环境
    ├── .env               # 配置文件 / 环境变量
    ├── .gitignore         # Git 忽略文件
    ├── requirements.txt   # 第三方依赖清单
    └── README.md          # 项目说明文档
```