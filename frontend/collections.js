let state={page:1,keyword:'',category:'',subcategory:'',period:''};let cats=[];let timeRange={min:new Date().getFullYear(),max:new Date().getFullYear()};
function esc(s){return String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))}
function buttons(arr,active){return arr.map(x=>`<button type="button" class="${x===active?'active':''}" data-v="${esc(x)}">${esc(x||'全部')}</button>`).join('')}
function makePeriods(min,max){if(!Number.isFinite(min)||!Number.isFinite(max)||min>max)return [];const out=[];let start=min;while(start<=max){const end=Math.min(Math.floor(start/10)*10+9,max);out.push(`${start}-${end}`);start=end+1}return out}
async function init(){try{const [c,r]=await Promise.all([fetch('/api/categories').then(x=>x.json()),fetch('/api/creation-time-range').then(x=>x.json())]);cats=c;timeRange={min:Number(r.min_year),max:Number(r.max_year)};renderFilters();load()}catch(e){document.getElementById('grid').innerHTML='<div class="empty">暂时无法读取作品</div>'}}
function renderFilters(){
  catFilter.innerHTML=buttons(['',...cats.map(x=>x.name)],state.category);
  const selected=cats.find(x=>x.name===state.category),subs=selected?.subs||[];
  const subRow=document.getElementById('subFilterRow');
  if(subs.length){subRow.hidden=false;subFilter.innerHTML=buttons(['',...subs],state.subcategory)}else{subRow.hidden=true;subFilter.innerHTML='';state.subcategory='';}
  const periods=makePeriods(timeRange.min,timeRange.max);
  periodFilter.innerHTML=buttons(['',...periods],state.period);
  document.querySelectorAll('.collection-page .filter button').forEach(b=>b.onclick=()=>{const box=b.parentElement.id,v=b.dataset.v;if(box==='catFilter'){state.category=v;state.subcategory=''}else if(box==='subFilter'){state.subcategory=v}else if(box==='periodFilter'){state.period=v}state.page=1;renderFilters();load()});
}
function load(){const q=new URLSearchParams({page:state.page,size:20,keyword:state.keyword,category:state.category,subcategory:state.subcategory,period:state.period});fetch('/api/works?'+q).then(r=>r.json()).then(d=>{count.textContent=`共 ${d.total} 件作品`;grid.innerHTML=d.items.length?d.items.map(x=>`<article class="work-card" onclick="location='/detail.html?id=${x.id}'"><div class="pic"><img src="${esc(x.main_image)}" alt="${esc(x.name||'')}"></div><h3>${esc(x.name)}</h3><p>${esc(x.category||'')}${x.subcategory?' · '+esc(x.subcategory):''}</p><p>${esc(x.work_no||'')}　${esc(x.creation_time||'')}</p></article>`).join(''):'<div class="empty">暂无符合条件的作品</div>';pages.innerHTML=Array.from({length:d.pages},(_,i)=>`<button type="button" class="${i+1===d.page?'active':''}" onclick="state.page=${i+1};load()">${i+1}</button>`).join('')}).catch(()=>{grid.innerHTML='<div class="empty">暂时无法读取作品</div>'})}
searchForm.onsubmit=e=>{e.preventDefault();state.keyword=keyword.value.trim();state.page=1;load()};init();
