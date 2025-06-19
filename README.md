# 📚 Flask电子图书馆管理系统

[![在线访问](https://img.shields.io/badge/Online-https%3A%2F%2Flibrary.yuelingxuan.cn-blue)](https://library.yuelingxuan.cn)
[![GitHub仓库](https://img.shields.io/badge/GitHub-Repository-brightgreen)](https://github.com/YUELINGXUAN0412/flask-library-system)
[![Docker镜像](https://img.shields.io/badge/Docker-yuelingxuan%2Flibrary--system%3A1.0-orange)](https://hub.docker.com/r/yuelingxuan/library-system)

## 📌 项目简介
本项目是一个功能完善的电子图书馆管理系统，实现了图书管理、借阅流通、用户服务等核心业务流程。系统采用Flask框架开发，支持多角色权限管理，完整模拟了从图书借阅申请到预约队列触发的全业务闭环。

## 🔑 权限体系
### 🧑‍🎓 普通用户
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

## 🚀 部署与运行
```bash
# 拉取镜像
docker pull yuelingxuan/library-system:1.0

# 启动容器
docker run -d -p 80:5000 yuelingxuan/library-system:1.0
