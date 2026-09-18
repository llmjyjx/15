const id=new URLSearchParams(location.search).get('id');
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
async function load(){
  const r=await apiFetch('api/works/'+encodeURIComponent(id));
  if(!r.ok){detail.innerHTML='<div class="empty">作品不存在</div>';return}
  const d=await r.json();
  document.title=(d.name||'作品详情')+' · 向攀艺术';
  const main=resolveAssetUrl(d.main_image_full||d.main_image||(d.images?.[0]?.url||''));
  detail.innerHTML=`<div class="detail-top"><div class="eyebrow">全部作品 / 作品详情</div><h1>${esc(d.name)}</h1></div><div class="detail-layout"><div><div class="detail-main-image">${main?`<img id="mainImg" src="${esc(main)}" alt="${esc(d.name)}">`:''}</div><div class="thumbs">${(d.images||[]).map(x=>`<img class="${x.is_main?'active':''}" src="${esc(resolveAssetUrl(x.thumb||x.url))}" alt="" data-full="${esc(resolveAssetUrl(x.url))}" onclick="showImg(this.dataset.full,this)">`).join('')}</div></div><aside><div class="meta"><div class="meta-row"><b>作品分类</b><span>${esc(d.category||'')}${d.subcategory?' / '+esc(d.subcategory):''}</span></div><div class="meta-row"><b>作品编号</b><span>${esc(d.work_no||'')}</span></div><div class="meta-row"><b>创作时间</b><span>${esc(d.creation_time||'')}</span></div><div class="meta-row"><b>尺寸</b><span>${esc(d.size||'')}</span></div></div><div class="description">${d.description||''}</div></aside></div>`
}
function showImg(u,el){document.getElementById('mainImg').src=resolveAssetUrl(u);document.querySelectorAll('.thumbs img').forEach(x=>x.classList.remove('active'));el.classList.add('active')}
load();
