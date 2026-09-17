(async function(){
  const el=document.getElementById('socialFooter');
  if(!el)return;
  try{
    const d=await apiFetch('api/site').then(r=>r.json());
    let social={微博:'',抖音:'',公众号:''};
    try{
      const raw=JSON.parse(d.social_links||'{}');
      if(Array.isArray(raw)){
        social.微博=raw[0]||''; social.抖音=raw[1]||''; social.公众号=raw[2]||'';
      }else if(raw&&typeof raw==='object'){
        social.微博=raw.微博||''; social.抖音=raw.抖音||''; social.公众号=raw.公众号||'';
      }
    }catch(e){}
    const order=[['微博',social.微博],['抖音',social.抖音],['公众号',social.公众号]];
    el.innerHTML=order.filter(x=>x[1]).map(x=>`<a href="${esc(x[1])}" target="_blank" rel="noopener noreferrer">${x[0]}</a>`).join('');
    el.hidden=!el.children.length;
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
