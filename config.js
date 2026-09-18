/* 向攀艺术 V51：本地 + Supabase 自动识别
 * local  = Flask + SQLite
 * cloud  = GitHub Pages + Edge Function + Postgres + Storage
 * auto   = localhost / 127.0.0.1 / file → 本地，其它 → 云端
 */
window.XIANGPAN_CONFIG = {
  mode: 'cloud',
  // 部署后改成你的项目：https://<PROJECT_REF>.supabase.co/functions/v1/api
  cloudApiBase: 'https://urwzkpqflmkzwssadvpw.supabase.co/functions/v1',
  localApiBase: 'http://127.0.0.1:5038',
  localOrigin: 'http://127.0.0.1:5038'
};
