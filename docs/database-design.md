# 📊 数据库结构设计

## 🛢 MySQL 表结构

### `users`
- `id`: 主键，整型
- `username`: 用户名
- `email`: 邮箱
- `password_hash`: 加密后的密码
- `created_at`: 注册时间

### `quizzes`
- `id`: 主键
- `user_id`: 外键，关联用户
- `title`: 题库标题
- `created_at`: 创建时间

### `questions`
- `id`: 主键
- `quiz_id`: 外键，关联题库
- `question_text`: 问题内容
- `options`: JSON 形式的选项
- `answer`: 正确答案

## 🍃 MongoDB 集合设计

### `content_chunks`
- `_id`: 自动生成
- `user_id`: 上传者
- `file_name`: 文件名
- `content_block`: 一段解析后的文本
- `type`: pdf/ppt/manual
- `created_at`: 时间戳

### `comments`
- `_id`: 评论ID
- `content_chunk_id`: 所属内容块
- `author_id`: 评论人
- `text`: 评论内容
- `timestamp`: 时间戳
