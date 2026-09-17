/* V33 统一 API 层：只修改 config.js 即可在本地 Flask / 云端 Worker 间切换 */
(function(){
  const cfg=window.XIANGPAN_CONFIG||{};
  function isLocalHost(){
    const h=location.hostname;
    return h==='localhost'||h==='127.0.0.1'||h==='0.0.0.0'||h==='::1';
  }
  const mode=String(cfg.mode||'auto').toLowerCase();
  const local=(mode==='local')||(mode==='auto'&&isLocalHost());
  const base=local?(cfg.localApiBase||''):(cfg.cloudApiBase||'');
  window.XIANGPAN_RUNTIME={mode:local?'local':'cloud',apiBase:base};
  const rawFetch=window.fetch.bind(window);
  window.fetch=async function(input,init){
    init=init||{};
    let url=typeof input==='string'?input:input.url;
    if(url.startsWith('/api/')) url=base.replace(/\/$/,'')+url;
    const headers=new Headers(init.headers||{});
    const token=localStorage.getItem('xiangpan_admin_token');
    if(token && url.includes('/api/admin/')) headers.set('Authorization','Bearer '+token);
    init.headers=headers;
    const res=await rawFetch(url,init);
    if(url.includes('/api/admin/login') && res.ok){
      try{const d=await res.clone().json();if(d.token)localStorage.setItem('xiangpan_admin_token',d.token)}catch(e){}
    }
    if(url.includes('/api/admin/logout')) localStorage.removeItem('xiangpan_admin_token');
    if(res.status===401 && url.includes('/api/admin/')) localStorage.removeItem('xiangpan_admin_token');
    return res;
  };
})();
