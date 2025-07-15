# 📊 数据库结构设计

## 🛢 MySQL 表设计

### users
- id: int, 主键，自增
- username: varchar
- email: varchar
- password_hash: varchar
- created_at: datetime

### speeches
- id: int, 主键
- user_id: 外键，关联用户
- title: varchar
- created_at: datetime

### questions
- id: int, 主键
- speech_id: 外键，关联演讲
- question_text: text
- options: json
- answer: varchar
- created_at: datetime

## 🍃 MongoDB 集合设计

### content_chunks
- _id: ObjectId
- user_id: string
- file_name: string
- content_block: string
- type: string (pdf/pptx/manual)
- created_at: datetime

### discussions
- _id: ObjectId
- chunk_id: 关联的 content_chunk
- author_id: 用户 ID
- text: string
- timestamp: datetime
