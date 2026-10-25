# AILT9019 Teammate Matcher - UI

纯前端 UI 界面，用于展示 Teammate Matcher 项目的用户界面。

## 文件结构

```
ui/
├── index.html          # 登录页面
├── register.html       # 注册页面
├── dashboard.html      # 主控制面板
├── results.html        # 匹配结果展示
├── edit-profile.html   # 编辑个人资料
├── css/
│   └── style.css       # 样式文件
├── js/
│   └── app.js          # JavaScript 逻辑
└── data/
    └── mock-data.json  # 模拟数据
```

## 使用方法

### 直接在浏览器打开

1. 打开 `index.html` 文件
2. 使用演示账号登录：
   - 用户名：`alice_chen`
   - 密码：`demo`

### 或使用本地服务器

```bash
# Python 3
cd ui
python -m http.server 8000

# 然后访问 http://localhost:8000
```

## 功能页面

### 1. 登录页 (index.html)
- 用户登录表单
- 演示账号提示
- 注册链接

### 2. 注册页 (register.html)
- 新用户注册表单
- 字段：用户名、密码、显示名、邮箱、城市、角色、语言

### 3. Dashboard (dashboard.html)
- 显示当前用户资料
- 运行匹配算法按钮
- 匹配流程说明

### 4. 匹配结果 (results.html)
- 统计数据（总人数、符合条件、被过滤、推荐人数）
- 过滤原因摘要
- 推荐队友列表（排名、角色、共同语言、匹配原因）
- 联系按钮

### 5. 编辑资料 (edit-profile.html)
- 修改个人资料
- 更新城市、角色、语言等信息

## 设计特点

- **响应式设计**：适配桌面和移动设备
- **现代化 UI**：使用卡片布局、渐变色彩、阴影效果
- **交互反馈**：表单验证、成功/错误提示
- **模拟数据**：使用 JSON 文件模拟后端数据

## 技术栈

- HTML5
- CSS3 (自定义样式，无框架)
- Vanilla JavaScript (无框架)
- LocalStorage (模拟用户会话)

## 注意事项

这是纯前端演示 UI，所有数据都是模拟的。实际项目中需要：
- 连接后端 API（由队友负责）
- 真实的用户认证系统
- 实际的匹配算法调用

## 截图

（可在浏览器中打开查看实际效果）

---

AILT9019 - AI Literacy for Computing and Data Science | HKU 2026-27
