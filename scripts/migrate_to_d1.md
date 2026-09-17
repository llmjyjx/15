# V32 云端迁移

## 1. 创建 D1

```bash
cd cloudflare-worker
npx wrangler d1 create xiangpan-art
```

把返回的 `database_id` 写入 `wrangler.toml`。

## 2. 创建 R2

```bash
npx wrangler r2 bucket create xiangpan-art
```

## 3. 初始化 D1 结构

```bash
npx wrangler d1 execute xiangpan-art --remote --file=schema.sql
```

## 4. 导入现有 SQLite 数据

`migration/art.sql` 是从 V31 `data/art.db` 导出的完整 SQL 数据。

```bash
npx wrangler d1 execute xiangpan-art --remote --file=../migration/art.sql
```

如果你已经执行过 `schema.sql`，SQL 中的 CREATE TABLE IF NOT EXISTS 可以安全重复执行；如遇到版本差异，先备份再导入。

## 5. 上传现有作品图片

V32 已经把演示图片放在 GitHub Pages 的 `frontend/img/details/` 中，所以演示作品无需 R2。

V31 中 `uploads/` 目录的历史上传图片需要单独上传到 R2。可以用 Wrangler 批量上传，或者根据自己的图片目录编写上传脚本。数据库中历史上传图片记录如果是 `r2/...`，Worker 会直接从 R2 提供。

## 6. 配置前端 API

编辑 `frontend/api.js`：

```js
window.XIANGPAN_API_BASE = 'https://你的-worker.workers.dev';
```

## 7. 配置 Worker

修改 `cloudflare-worker/wrangler.toml`：

- `FRONTEND_ORIGIN`：GitHub Pages 地址
- `database_id`：D1 ID

然后：

```bash
npx wrangler deploy
```

## 8. GitHub Pages

把 `frontend/` 目录作为 GitHub Pages 发布目录即可。

如果使用自定义域名，可以把 Pages 设置为 `www.example.com`，API 使用 `api.example.com`。GitHub Pages 官方支持 `www`、其他子域名和 apex 域名。 

## 默认超级管理员

数据库迁移会保留现有 V31 的 `admin` 超级管理员哈希：

- 账号：`admin`
- 初始密码：`admin123`
- 权限：超级管理员

V32 登录使用 Web Crypto PBKDF2-SHA256 验证现有 Werkzeug PBKDF2 哈希，不需要把密码改成明文或 MD5。
