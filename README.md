# Multimodal Quiz Generation Platform

🎯 一个用于解析 PDF/PPT 内容并自动生成题目的 AI 平台。

## 📦 技术栈

- **后端**: Python + FastAPI
- **前端**: Vue 3 + Vite
- **数据库**: MySQL + MongoDB

## 📁 项目结构

```
multimodal-quiz-project/
├── backend/      # 后端服务
├── frontend/     # 前端界面
├── docs/         # 文档资料
├── .vscode/      # VSCode 配置
├── README.md
```

## 🚀 启动方式

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 👥 小组成员

- 程旭：文件解析、数据库设计
- 王家宝：AI生成与上下文管理
- 卢汉：前端、用户与讨论功能
- 袁智涵：文档管理、测试与优化

## ✅ Git 工作流程

- 主分支为 `main`，禁止直接提交
- 功能分支命名规则：`feature/功能名-拼音名`
- Git 提交信息格式：

```bash
feat: 实现了文件上传功能
```
