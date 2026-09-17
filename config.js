/* 向攀艺术 V38：前后端分离 / 本地 + Supabase 云端自动识别
 * local  = 本地前端 + Flask API + SQLite
 * cloud  = GitHub Pages + Supabase Edge Function + Postgres + Storage
 * auto   = localhost / 127.0.0.1 / file 协议自动本地，其它正式域名自动云端
 */
window.XIANGPAN_CONFIG = {
  mode: 'auto',
  // Supabase Edge Function 完成部署后填写：
  // https://你的项目ID.supabase.co/functions/v1/api
  cloudApiBase: 'https://urwzkpqflmkzwssadvpw.supabase.co/functions/v1/api',
  // 本地 Flask 默认 5038
  localApiBase: 'http://127.0.0.1:5038',
  localOrigin: 'http://127.0.0.1:5038'
};
