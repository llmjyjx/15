let slides=[],idx=0,timer;
async function load(){
  const [s,r]=await Promise.all([apiFetch('api/site').then(x=>x.json()),apiFetch('api/home/random').then(x=>x.json())]);
  const artist=(s.artist_name||'').trim();
  artistName.textContent=artist;
  artistName.hidden=!artist;
  const bio=(s.artist_bio||'').trim();
  artistBio.dataset.appManaged='1';
  artistBio.innerHTML=bio;
  artistBio.hidden=!bio;
  const av=(s.avatar||'').trim();
  if(av){
    avatar.src=resolveAssetUrl(av);
    avatar.alt=artist||'';
    avatar.hidden=false;
  }else{
    avatar.removeAttribute('src');
    avatar.alt='';
    avatar.hidden=true;
  }
  slides=r.filter(x=>(x.main_image||'').trim());
  const hero=document.querySelector('.hero');
  if(hero) hero.hidden=!slides.length;
  render();
  if(slides.length) timer=setInterval(next,4500)
}
function render(){slidesEl.innerHTML=slides.map((x,i)=>`<a class=\"hero-slide ${i===idx?'active':''}\" href=\"detail.html?id=${x.id}\"><img src=\"${resolveAssetUrl(x.main_image)}\" alt=\"${x.name||''}\"></a>`).join('');caption.textContent=slides[idx]?.name||''}
function next(){if(!slides.length)return;idx=(idx+1)%slides.length;render()}
function prev(){if(!slides.length)return;idx=(idx-1+slides.length)%slides.length;render()}
const slidesEl=document.getElementById('slides'),caption=document.getElementById('caption');
document.getElementById('next').onclick=next;document.getElementById('prev').onclick=prev;load();
