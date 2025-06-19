# 📚 Flask电子图书馆管理系统

[![在线访问](https://img.shields.io/badge/Online-https%3A%2F%2Flibrary.yuelingxuan.cn-blue)](https://library.yuelingxuan.cn)
[![GitHub仓库](https://img.shields.io/badge/GitHub-Repository-brightgreen)](https://github.com/YUELINGXUAN0412/flask-library-system)
[![Docker镜像](https://img.shields.io/badge/Docker-yuelingxuan%2Flibrary--system%3A1.0-orange)](https://hub.docker.com/r/yuelingxuan/library-system)

## 📌 项目简介
本项目是一个功能完善的电子图书馆管理系统，实现了图书管理、借阅流通、用户服务等核心业务流程。系统采用Flask框架开发，支持多角色权限管理，完整模拟了从图书借阅申请到预约队列触发的全业务闭环。

## 🔑 权限体系
### 🧑 普通用户
- 图书浏览/搜索/筛选
- 在线提交借阅/预约申请
- 借阅历史与预约状态管理
- 个人资料维护（含头像上传）

### 👨‍💻 管理员
- 图书/分类/用户管理
- 借阅/归还/预约审批处理
- 运营数据统计分析
- 系统日志查看

### 👑 超级管理员
- 管理员账号管理
- 系统核心参数配置
- 全局权限管控

## 🌟 主要亮点
✅ 完整的图书流通业务闭环  
✅ 响应式设计适配多设备  
✅ 头像上传与用户中心交互  
✅ 可视化运营数据看板  
✅ Docker容器化部署支持

## 🐳 使用Docker Compose部署
```yaml
services:
  web:
    image: yuelingxuan/library-system:latest
    container_name: library_web
    restart: unless-stopped
    ports:
      - "127.0.0.1:5000:5000"
    volumes:
      - ./uploads:/app/app/static/uploads
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=a-very-long-and-random-secret-key-that-you-should-change
      - DB_USER=root
      - DB_PASSWORD=mysecretpassword
      - DB_HOST=db
      - DB_PORT=3306
      - DB_NAME=library_db
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - ADMIN_DEFAULT_PASSWORD=admin123
      - UPLOAD_FOLDER=/app/app/static/uploads/covers
      - AVATAR_UPLOAD_FOLDER=/app/app/static/uploads/avatars
    depends_on:
      - db
      - redis
    networks:
      - library_net

  db:
    image: mysql:8.0
    container_name: library_db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: mysecretpassword
      MYSQL_DATABASE: library_db
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - library_net

  redis:
    image: redis:6-alpine
    container_name: library_redis
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - library_net

networks:
  library_net:
    driver: bridge

volumes:
  db_data:
  redis_data:
