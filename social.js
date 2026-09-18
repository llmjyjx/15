(async function(){
  const el=document.getElementById('socialFooter');
  if(!el)return;
  const KEYS=['微博','微信','小程序','学习强国号','视频号','抖音号'];
  const ICONS={
    '微博':'<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M10.1 17.6c-3.3.5-6.1-1.2-6.3-3.7-.2-2.5 2.3-5 5.6-5.5 3.3-.5 6.1 1.2 6.3 3.7.2 2.5-2.3 5-5.6 5.5zm1.3-8.5c-4.1.4-7.2 3.1-6.9 6.1.3 3 3.9 5.1 8 4.7 4.1-.4 7.2-3.1 6.9-6.1-.3-3-3.9-5.1-8-4.7zm7.3-1.6c-.2-.7-.8-1.2-1.5-1.3-.3 0-.5-.2-.5-.5s.2-.5.5-.5c1.1.1 2.1.9 2.5 2 .1.3 0 .6-.3.7-.3.1-.6 0-.7-.4zm1.6-3.1c-1.3-1.5-3.2-2.4-5.2-2.5-.3 0-.6-.3-.6-.6s.3-.6.6-.6c2.5.1 4.8 1.2 6.4 3.1.2.2.2.6 0 .8-.2.2-.6.2-.8 0-.1-.1-.2-.2-.4-.2zM9.8 12.3c-.9.2-1.5.8-1.4 1.5.1.7.9 1.2 1.8 1.1.9-.1 1.5-.8 1.4-1.5-.1-.7-.9-1.2-1.8-1.1zm5.3.5c-.2-.5-.7-.8-1.3-.7-.5.1-.9.5-.9 1 0 .5.4.9.9 1 .6.1 1.1-.2 1.3-.7.1-.2 0-.4-.2-.5-.1 0-.2 0-.3.1-.1.1-.2.2-.3.2-.2 0-.3-.1-.3-.3 0-.2.2-.3.4-.4.2 0 .4.1.5.3.1.2.3.2.5.1.1-.1.2-.2.2-.4z"/></svg>',
    '微信':'<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M9.5 4C5.9 4 3 6.5 3 9.6c0 1.8 1 3.4 2.5 4.4l-.6 2.2 2.5-1.3c.7.2 1.4.3 2.1.3.2 0 .4 0 .6 0-.2-.5-.3-1.1-.3-1.6 0-3.3 3.1-6 6.9-6 .2 0 .5 0 .7.1C16.6 5.4 13.4 4 9.5 4zm-2.3 3.2c.5 0 .9.4.9.9s-.4.9-.9.9-.9-.4-.9-.9.4-.9.9-.9zm4.1 0c.5 0 .9.4.9.9s-.4.9-.9.9-.9-.4-.9-.9.4-.9.9-.9zM16.6 10c-3.2 0-5.8 2.2-5.8 4.9 0 2.7 2.6 4.9 5.8 4.9.7 0 1.3-.1 1.9-.3l2.2 1.1-.5-1.9c1.3-.9 2.1-2.2 2.1-3.8 0-2.7-2.6-4.9-5.7-4.9zm-2 3c.4 0 .7.3.7.7s-.3.7-.7.7-.7-.3-.7-.7.3-.7.7-.7zm4 0c.4 0 .7.3.7.7s-.3.7-.7.7-.7-.3-.7-.7.3-.7.7-.7z"/></svg>',
    '小程序':'<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M12 3c-1.7 0-3 1.6-3 3.5v2.2c0 .4-.3.7-.7.7H6.5C4.6 9.4 3 10.7 3 12.4s1.6 3 3.5 3h1.8c.4 0 .7.3.7.7v1.4c0 1.9 1.3 3.5 3 3.5s3-1.6 3-3.5v-1.4c0-.4.3-.7.7-.7h1.8c1.9 0 3.5-1.3 3.5-3s-1.6-3-3.5-3h-1.8c-.4 0-.7-.3-.7-.7V6.5C15 4.6 13.7 3 12 3zm0 1.5c.8 0 1.5.9 1.5 2v2.2c0 1.2.9 2.2 2.2 2.2h1.8c1.1 0 2 .7 2 1.5s-.9 1.5-2 1.5h-1.8c-1.3 0-2.2 1-2.2 2.2v1.4c0 1.1-.7 2-1.5 2s-1.5-.9-1.5-2v-1.4c0-1.2-.9-2.2-2.2-2.2H6.5c-1.1 0-2-.7-2-1.5s.9-1.5 2-1.5h1.8c1.3 0 2.2-1 2.2-2.2V6.5c0-1.1.7-2 1.5-2z"/></svg>',
    '学习强国号':'<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M6 4h12v2H6V4zm0 4h12v2H6V8zm0 4h8v2H6v-2zm0 4h10v2H6v-2z"/><circle cx="18" cy="15" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
    '视频号':'<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M4 6.5A2.5 2.5 0 016.5 4h11A2.5 2.5 0 0120 6.5v11a2.5 2.5 0 01-2.5 2.5h-11A2.5 2.5 0 014 17.5v-11zM10 9.2v5.6l5-2.8-5-2.8z"/></svg>',
    '抖音号':'<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M14.5 3c.3 2.2 1.6 3.7 3.8 4.1v2.4c-1.3-.1-2.5-.5-3.5-1.2v6.3c0 3.2-2.5 5.4-5.6 5.4S3.6 17.8 3.6 14.6c0-3 2.2-5.2 5.2-5.4v2.5c-1.4.2-2.4 1.2-2.4 2.8 0 1.7 1.2 2.9 2.9 2.9 1.8 0 2.9-1.2 2.9-3.1V3h2.3z"/></svg>'
  };
  try{
    const d=await apiFetch('api/site').then(r=>r.json());
    let social={};
    KEYS.forEach(k=>social[k]='');
    try{
      const raw=JSON.parse(d.social_links||'{}');
      if(Array.isArray(raw)){
        social['微博']=raw[0]||'';
        social['抖音号']=raw[1]||'';
        social['微信']=raw[2]||'';
      }else if(raw&&typeof raw==='object'){
        social['微博']=raw['微博']||'';
        social['微信']=raw['微信']||raw['公众号']||'';
        social['小程序']=raw['小程序']||'';
        social['学习强国号']=raw['学习强国号']||'';
        social['视频号']=raw['视频号']||'';
        social['抖音号']=raw['抖音号']||raw['抖音']||'';
      }
    }catch(e){}
    const items=KEYS.filter(k=>social[k]).map(k=>{
      const url=esc(social[k]);
      const icon=ICONS[k]||'';
      return `<a class="social-item" href="${url}" target="_blank" rel="noopener noreferrer" title="${esc(k)}"><span class="social-icon">${icon}</span><span class="social-label">${esc(k)}</span></a>`;
    });
    el.innerHTML=items.join('');
    el.hidden=!items.length;
  }catch(e){el.hidden=true;}
  function esc(s){return String(s??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;')}
})();

;(function(){
  let n=0,t=0;
  function bind(){
    document.querySelectorAll('#copyrightTap, .copyright-tap').forEach(el=>{
      if(el.dataset.tapBound) return;
      el.dataset.tapBound='1';
      el.style.cursor='default';
      el.addEventListener('click', function(){
        const now=Date.now();
        if(now-t>1500)n=0;
        t=now; n++;
        if(n>=3){n=0; location.href='admin.html';}
      });
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', bind);
  else bind();
})();
