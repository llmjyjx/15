/* 向攀艺术 V33 本地 / 云端切换配置
 * mode: 'local'  本机 Flask + SQLite
 * mode: 'cloud'  GitHub Pages + Cloudflare Worker
 * mode: 'auto'   localhost 自动本地，其它域名自动云端
 */
window.XIANGPAN_CONFIG = {
  mode: 'auto',
  cloudApiBase: 'https://YOUR-WORKER.YOUR-SUBDOMAIN.workers.dev',
  localApiBase: '',
  localOrigin: 'http://127.0.0.1:5033'
};
