const $ = id => document.getElementById(id);
const SPORT_NAMES = {cfb:'College football',nfl:'NFL',soccer:'Soccer',nba:'NBA',mlb:'MLB',cbb:'College basketball'};
let initialized = false;
async function api(path, data){const r=await fetch(path,{method:data===undefined?'GET':'POST',headers:{'Content-Type':'application/json'},body:data===undefined?undefined:JSON.stringify(data)});const j=await r.json();if(!r.ok)throw Error(j.error||'Request failed');return j;}
function node(tag,text,cls){const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;}
function render(data){
  const selected = data.games.find(x=>x.game.id===data.current_id);
  $('headline').textContent=selected?`${selected.game.away} vs ${selected.game.home}`:'No eligible live games';
  $('bigscore').textContent=selected?`${selected.game.away_score} – ${selected.game.home_score}`:'—';
  $('details').textContent=selected?`${selected.game.sport.toUpperCase()}  ·  ${selected.game.period}  ·  ${selected.game.clock}  ·  ${selected.game.channel}`:'';
  $('reason').textContent=data.reason;
  $('games').replaceChildren();
  for(const entry of data.games){const g=entry.game;const row=node('div',undefined,'game');const main=node('div',undefined,'game-main');main.append(node('div',`${g.away} vs ${g.home}`,'game-name'),node('div',`${SPORT_NAMES[g.sport]} · ${g.period} · ${g.clock}`,'game-meta'));
    const side=node('div',undefined,'game-side');side.append(node('span',`${g.away_score}–${g.home_score}`,'score'),node('span',`${entry.score} pts`,'rank'));
    if(g.id===data.current_id)side.append(node('span','SELECTED','selected'));else{const b=node('button','Select');b.onclick=()=>api('/api/select',{id:g.id}).then(render).catch(showError);side.append(b);}row.append(main,side);$('games').append(row);
  }
  $('events').replaceChildren();for(const event of data.events){const line=node('div');const stamp=node('b',event.at+'  ');line.append(stamp,document.createTextNode(`${event.game} — ${event.reason}`));$('events').append(line);}
  if(!initialized){$('favorites').value=data.settings.favorite_teams.join(', ');$('auto').checked=data.settings.auto_mode;$('favoriteFirst').checked=data.settings.favorite_first;$('cooldown').value=data.settings.min_seconds_between_switches;
    $('sports').replaceChildren();for(const [key,label] of Object.entries(SPORT_NAMES)){const wrap=node('label');const cb=document.createElement('input');cb.type='checkbox';cb.value=key;cb.checked=data.settings.sports.includes(key);wrap.append(cb,document.createTextNode(' '+label));$('sports').append(wrap);}initialized=true;}
}
function showError(err){alert(err.message);}
$('save').onclick=async()=>{try{await api('/api/settings',{favorite_teams:$('favorites').value.split(',').map(x=>x.trim()).filter(Boolean),auto_mode:$('auto').checked,favorite_first:$('favoriteFirst').checked,min_seconds_between_switches:Number($('cooldown').value),sports:[...$('sports').querySelectorAll('input:checked')].map(x=>x.value)});render(await api('/api/state'));}catch(e){showError(e);}};
$('advance').onclick=async()=>{try{await api('/api/advance',{});render(await api('/api/state'));}catch(e){showError(e);}};
$('fullscreen').onclick=()=>{if(!document.fullscreenElement)document.documentElement.requestFullscreen?.();else document.exitFullscreen?.();};
$('clock').textContent=new Date().toLocaleTimeString();setInterval(()=>{$('clock').textContent=new Date().toLocaleTimeString();},1000);
async function refresh(){try{render(await api('/api/state'));}catch(e){console.error(e);}}
refresh();setInterval(refresh,3000);
