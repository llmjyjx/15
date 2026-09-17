# 向攀书法艺术网站 V33：本地 + 云端统一版

## 一套前端，通过一个配置文件切换

配置文件：`frontend/config.js`

### 本地
```js
window.XIANGPAN_CONFIG = {
  mode: 'local',
  cloudApiBase: 'https://YOUR-WORKER.YOUR-SUBDOMAIN.workers.dev',
  localApiBase: '',
  localOrigin: 'http://127.0.0.1:5033'
};
```

本地使用：Flask + SQLite，启动 `启动网站.bat`，访问 `http://127.0.0.1:5033/`。

### 云端
```js
mode: 'cloud'
```
并把 `cloudApiBase` 改为你的 Cloudflare Worker 地址。前端可直接发布到 GitHub Pages。

### 自动
默认 `mode: 'auto'`：localhost / 127.0.0.1 自动使用本地 Flask，其它域名自动使用 Cloudflare Worker。

## 数据
- 本地：`data/art.db`
- 云端：Cloudflare D1
- 云端图片：Cloudflare R2
- D1 导入：`migration/art.sql`

## 本地端口
V33 = 5033。

## 云端部署
详见 `scripts/migrate_to_d1.md` 和 `cloudflare-worker/README.md`。

## 重要
本地和云端使用同一套 frontend 页面；切换后端只需要修改 `frontend/config.js`，无需修改业务页面 JS。
"# 15" 
