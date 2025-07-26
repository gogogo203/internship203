# PopQuiz - 实时互动测验系统
## 📖 项目简介
PopQuiz 是一款面向课堂、培训与会议的实时互动测验系统。以 AI 自动生成测验为核心功能，能够在演讲/授课过程中快速生成随堂测验，并通过 Web 端实时推送给听众。

### ✨ 核心特性
- 🤖 AI 智能出题 ：基于智谱AI，自动从上传文档生成高质量选择题
- 📁 多格式支持 ：支持 PPT、PDF、TXT 文件解析
- 👥 多角色管理 ：支持管理员、教师、学生三种角色
- 📊 实时统计 ：实时查看答题情况和统计分析
- 💬 反馈系统 ：支持演讲反馈和评分功能
- 🎨 现代UI ：采用现代CSS3技术，界面美观流畅
## 🏗️ 技术架构
### 后端技术栈
- Flask 2.0.1 - Web框架
- SQLAlchemy - ORM数据库操作
- SQLite - 轻量级数据库
- 智谱AI API - AI问题生成服务
- python-pptx - PowerPoint文件处理
- PyPDF2 - PDF文件处理
- bcrypt - 密码加密
### 前端技术栈
- HTML5 + CSS3 - 页面结构和样式
- 原生JavaScript - 交互逻辑
- Flask Jinja2 - 模板引擎
- 响应式设计 - 支持多设备访问
### 项目结构
```
popquiz-project/
├── app.py                 # 应用入口文件
├── requirements.txt       # 依赖包列表
├── .env                  # 环境变量配置
├── backend/              # 后端模块
│   ├── __init__.py       # Flask应用工厂
│   ├── config.py         # 配置文件
│   ├── models.py         # 数据模型
│   ├── database.py       # 数据库初始化
│   ├── ai_service.py     # AI服务模块
│   ├── file_processor.py # 文件处理模块
│   ├── auth.py          # 认证模块
│   └── routes/          # 路由模块
│       ├── auth.py      # 认证路由
│       ├── main_routes.py
│       ├── user_routes.py
│       ├── quiz_routes.py
│       ├── presentation_routes.py
│       └── feedback_routes.py
├── front/               # 前端资源
│   ├── html/           # HTML模板
│   ├── css/            # 样式文件
│   ├── js/             # JavaScript文件
│   └── static/         # 静态资源
├── instance/           # 实例文件夹
│   └── popquiz.db     # SQLite数据库
└── uploads/           # 文件上传目录
```
## 🚀 快速开始
### 环境要求
- Python 3.8+
- pip 包管理器
### 安装步骤
1. 1.
   克隆项目
```
git clone <repository-url>
cd popquiz-project
```
2. 1.
   创建虚拟环境
```
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```
3. 1.
   安装依赖
```
pip install -r requirements.txt
```
4. 1.
   配置环境变量
创建 .env 文件并添加以下配置：

```
ZHIPU_API_KEY=your_zhipu_ai_api_key
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///popquiz.db
```
5. 1.
   运行应用
```
python app.py
```
6. 1.
   访问应用
打开浏览器访问： http://localhost:5000

### 默认账户
- 管理员 : organizer / password
- 教师 : teacher / password
- 学生 : audience / password
## 📋 功能模块
### 1. 用户管理
- 用户注册与登录
- 角色权限管理（管理员/教师/学生）
- 用户信息管理
### 2. 演讲管理
- 创建和管理演讲
- 演讲详情查看
- 演讲状态控制
### 3. 测验系统
- 文件上传（PPT/PDF/TXT）
- AI自动生成选择题
- 实时答题功能
- 答题结果统计
### 4. 反馈系统
- 演讲评分（1-5星）
- 文字反馈
- 匿名反馈支持
- 反馈统计分析
## 🔧 配置说明
### 智谱AI配置
1. 1.
   注册智谱AI账号： https://open.bigmodel.cn/
2. 2.
   获取API密钥
3. 3.
   在 .env 文件中设置 ZHIPU_API_KEY
### 文件上传配置
- 支持格式： .txt , .pdf , .ppt , .pptx
- 最大文件大小：32MB
- 上传目录： uploads/
### 数据库配置
- 默认使用SQLite数据库
- 数据库文件： instance/popquiz.db
- 支持其他数据库（通过修改DATABASE_URL）
## 🎯 使用流程
### 教师端操作流程
1. 1.
   登录系统（使用teacher账户）
2. 2.
   创建新演讲
3. 3.
   上传课件文件（PPT/PDF/TXT）
4. 4.
   系统自动生成测验题目
5. 5.
   发布测验给学生
6. 6.
   查看答题统计和反馈
### 学生端操作流程
1. 1.
   登录系统（使用audience账户）
2. 2.
   查看可用的测验
3. 3.
   参与答题
4. 4.
   查看答题结果
5. 5.
   提交演讲反馈
## 🛠️ 开发指南
### 添加新功能
1. 1.
   在 backend/models.py 中定义数据模型
2. 2.
   在 backend/routes/ 中添加路由处理
3. 3.
   在 front/html/ 中添加页面模板
4. 4.
   在 front/css/ 和 front/js/ 中添加样式和交互
### 数据库迁移
```
# 如果需要修改数据库结构
flask db init
flask db migrate -m "描述信息"
flask db upgrade
```
### 调试模式
应用默认在调试模式下运行，修改代码后会自动重载。

## 📊 API 接口
### 认证接口
- POST /auth/login - 用户登录
- POST /auth/register - 用户注册
- GET /auth/logout - 用户登出
### 测验接口
- POST /upload - 上传文件生成测验
- GET /quiz/<id> - 获取测验详情
- POST /quiz/<id>/submit - 提交答案
- GET /quiz/<id>/results - 查看结果
### 反馈接口
- POST /feedback/submit - 提交反馈
- GET /feedback/<presentation_id> - 查看反馈
## 🔒 安全特性
- 密码bcrypt加密存储
- Session会话管理
- 文件类型验证
- SQL注入防护
- XSS攻击防护
## 🐛 常见问题
### Q: 智谱AI调用失败怎么办？
A: 检查API密钥是否正确设置，网络连接是否正常，API配额是否充足。

### Q: 文件上传失败？
A: 检查文件格式是否支持，文件大小是否超过32MB限制。

### Q: 数据库连接错误？
A: 检查数据库文件权限，确保instance目录存在且可写。

## 📝 更新日志
### v1.0.0 (2024-01-XX)
- 初始版本发布
- 基础测验功能
- AI自动出题
- 用户管理系统
- 反馈功能
需自行添加.env文件配置密钥

# 智谱AI API密钥
# 在此处填入您的智谱AI API密钥
# 获取方式：https://open.bigmodel.cn/usercenter/apikeys
ZHIPU_API_KEY="4c9c9b8d8f534938bb92e120c86e5eb2.PQfn79GzvvblFaz7"
