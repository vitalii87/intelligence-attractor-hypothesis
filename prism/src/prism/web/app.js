'use strict';
const $ = id => document.getElementById(id);
const el = (tag, text, cls) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; if (cls) n.className = cls; return n; };
const labels = {accepted:'Прийнято',rejected:'Відхилено',failed:'Помилка',interrupted:'Перервано',running:'Виконується',paused:'На паузі',complete:'Завершено',verified:'Перевірено',partial:'Неповний запис',error:'Помилка перевірки',unavailable:'Немає даних',pending:'Очікуємо запис',not_measured:'Не виміряно',read:'Прочитано'};
const eventNames = {lineage_created:'Створено лінію',workspace_initialized:'Підготовлено робочий простір',attempt_started:'Початок спроби',provider_call_started:'Запит до моделі',provider_call_completed:'Відповідь моделі',budget_charged:'Облік ресурсів',tool_called:'Виклик інструмента',tool_completed:'Результат інструмента',tool_result:'Результат інструмента',candidate_submitted:'Кандидат поданий',evaluation_completed:'Оцінювання завершено',attempt_accepted:'Кандидат прийнятий',attempt_rejected:'Кандидат відхилений',candidate_accepted:'Кандидат прийнятий',candidate_rejected:'Кандидат відхилений',artifact_created:'Артефакт збережений',attempt_completed:'Спробу завершено'};
const stopNames = {plateau:'Плато: нові спроби не покращують результат',max_epochs:'Досягнуто ліміту епох',budget_exhausted:'Вичерпано доступний бюджет',failure_limit:'Досягнуто ліміту помилок'};
const badge = value => el('span', labels[value] || value || '—', 'badge ' + (labels[value] ? value : ''));
const number = value => value == null ? '—' : new Intl.NumberFormat('uk-UA').format(value);
const pct = value => value == null ? '—' : new Intl.NumberFormat('uk-UA',{style:'percent',maximumFractionDigits:1}).format(value);
const money = value => value == null ? '—' : '$' + (value / 1e6).toFixed(value === 0 ? 2 : 4);
let data = null, runs = [], key = '0', serial = 0, tab = 'overview', selectedAttempt = null, eventLimit = 100;
const views = {
  overview: ['Огляд запуску', 'Результати, прогрес і ресурси — в одному місці.', 'Огляд'],
  attempts: ['Спроби та рішення', 'Простежте, що змінив агент і чому кандидат був прийнятий або відхилений.', 'Спроби'],
  events: ['Журнал подій', 'Від запиту до моделі до оцінювання — досліджуйте перебіг кожної спроби.', 'Журнал подій'],
  versions: ['Версії коду', 'Порівнюйте збережені знімки та переглядайте конкретні зміни.', 'Версії коду'],
  evidence: ['Контекст і докази', 'Умови експерименту, джерела даних та результати перевірок.', 'Контекст і докази']
};
const routeFields = {lineage:'lineage', status:'status-filter', search:'attempt-search', order:'attempt-order', query:'event-search', job:'event-attempt', type:'event-type', before:'version-before', after:'version-after', metric:'chart-metric'};
const activeLineage = () => data?.lineages.find(l => l.id === $('lineage').value) || data?.lineages[0];
const scoped = () => data ? data.attempts.filter(a => a.lineage === activeLineage()?.id) : [];
const sum = (a,b) => a == null || b == null ? null : a+b;
function empty(target, message) { target.replaceChildren(el('div',message,'empty')); }
function option(value, text) { const n=el('option',text); n.value=value; return n; }
function setTab(name, write = true) {
  tab = Object.hasOwn(views, name) ? name : 'overview';
  document.querySelectorAll('[data-tab]').forEach(b => {
    b.classList.toggle('active', b.dataset.tab === tab);
    if (b.dataset.tab === tab) b.setAttribute('aria-current', 'page');
    else b.removeAttribute('aria-current');
  });
  document.querySelectorAll('.tab-panel').forEach(p => p.hidden = p.id !== tab);
  [$('page-title').textContent, $('page-description').textContent, $('breadcrumb-view').textContent] = views[tab];
  document.title = `${views[tab][2]} · PRISM`;
  if (write) { saveRoute(); setMenu(false); window.scrollTo({top:0}); }
}
function saveRoute(replace = false) {
  const params = new URLSearchParams({view:tab, run:key});
  for (const [field, id] of Object.entries(routeFields)) if ($(id).value) params.set(field, $(id).value);
  if (selectedAttempt) params.set('attempt', selectedAttempt);
  const hash = '#' + params.toString();
  if (location.hash !== hash) history[replace ? 'replaceState' : 'pushState'](null, '', hash);
}
async function applyLocation() {
  const params = new URLSearchParams(location.hash.slice(1));
  key = runs.some(r => r.key === params.get('run')) ? params.get('run') : runs[0]?.key || '0';
  closeDetail(false);
  setTab(params.get('view'), false);
  renderRuns();
  if (!await refresh({lineage:params.get('lineage')})) return;
  for (const [field, id] of Object.entries(routeFields)) {
    const value = params.get(field), control = $(id);
    if (control.tagName === 'SELECT') {
      if (value !== null && [...control.options].some(o => o.value === value)) control.value = value;
      else if (!['lineage','version-before','version-after'].includes(id)) control.selectedIndex = 0;
    } else control.value = value || '';
  }
  render();
  const attempt = scoped().find(a => a.id === params.get('attempt'));
  if (attempt) renderDetail(attempt.id, true, false);
  saveRoute(true);
}
async function getJSON(url) { const r=await fetch(url,{cache:'no-store'}); const value=await r.json(); if(!r.ok)throw new Error(value.error || 'Помилка читання'); return value; }
async function refresh({lineage} = {}) {
  const request=++serial, current=key; $('refresh').disabled=true;
  try {
    const result=await getJSON('/api/run?id='+encodeURIComponent(current));
    if(request!==serial)return false;
    data=result; $('error').hidden=true; $('content').hidden=false; $('export').disabled=false;
    const prev=lineage ?? $('lineage').value;
    $('lineage').replaceChildren(...data.lineages.map(l=>option(l.id,l.id)));
    if(data.lineages.some(l=>l.id===prev))$('lineage').value=prev;
    $('run-title').textContent=data.name;
    $('subtitle').textContent=`${data.task} · Arena ${data.arena_version} · ${data.lineages.length} лінія / ліній`;
    $('prism-version').textContent='PRISM '+data.prism_version;
    $('run-status').replaceChildren(badge(data.status));
    $('updated').textContent='Оновлено '+new Date().toLocaleTimeString('uk-UA');
    $('warnings').replaceChildren(...data.warnings.map(w=>el('div',w,'notice')));
    render();
    if($('detail').open && selectedAttempt)renderDetail(selectedAttempt,false);
    return true;
  } catch(error) {
    if(request!==serial)return;
    $('error').textContent=error.message; $('error').hidden=false; $('content').hidden=true; $('export').disabled=true;
    $('updated').textContent='Не вдалося оновити'; $('run-status').replaceChildren(badge('error'));
  } finally { if(request===serial)$('refresh').disabled=false; }
}
function renderRuns() {
  $('run-count').textContent=runs.length;
  const query = $('run-search').value.toLocaleLowerCase().trim();
  const found = runs.filter(r => r.name.toLocaleLowerCase().includes(query));
  $('runs').replaceChildren(...found.map(r => {
    const b = el('button', r.name);
    b.classList.toggle('selected', r.key === key);
    if (r.key === key) b.setAttribute('aria-current', 'true');
    b.title = r.source;
    b.append(el('small', 'Arena · локальний запуск'));
    b.onclick = async () => {
      if (r.key === key) return;
      closeDetail(false); key = r.key; data = null;
      resetFilters(); $('lineage').replaceChildren();
      $('content').hidden = true; $('run-title').textContent = r.name;
      $('subtitle').textContent = 'Завантаження…'; renderRuns(); setMenu(false);
      if (await refresh()) saveRoute();
    };
    return b;
  }));
  if (!found.length) empty($('runs'), 'Запусків не знайдено');
}
function render() {
  const line=activeLineage(), rows=scoped(), done=rows.filter(a=>a.status!=='running');
  if (!line) { $('content').hidden = true; return; }
  let quality=rows.length?rows[0].baseline:null;
  for(const a of rows)if(a.status==='accepted')quality=a.quality;
  const accepted=rows.filter(a=>a.status==='accepted').length;
  const cards=[['Якість прийнятого рішення',pct(quality),'На selection suite · остання прийнята версія','◈'],['Спроби',String(done.length),`${accepted} прийнято · ${done.length-accepted} інших результатів`,'↗'],['Облік вартості',money(line.usage.cost_microusd),`Ліміт ${money(line.limits.cost_microusd)} · оцінка за тарифами`,'$'],['Токени',number(sum(line.usage.input_tokens,line.usage.output_tokens)),`${number(line.usage.input_tokens)} вхід · ${number(line.usage.output_tokens)} вихід`,'≋']];
  $('cards').replaceChildren(...cards.map((c,i)=>{const n=el('article',undefined,'card');const label=el('div',c[0],'card-label');label.append(el('span',c[3],'card-mark'));n.append(label,el('div',c[1],'card-value'+(i===0?' accent':'')),el('div',c[2],'card-sub'));return n;}));
  $('attempt-count').textContent=rows.length;
  $('event-count').textContent=number(rows.reduce((n,a)=>n+a.events.length,0));
  $('version-count').textContent=data.versions.filter(v=>v.lineage===line.id).length;
  const story = el('div');
  story.append(el('h2', data.status === 'complete' ? 'Запуск завершено' : labels[data.status] || 'Перебіг запуску'),
    el('p', `${accepted} прийнято з ${done.length} завершених спроб. ${stopNames[line.stop_reason] || line.stop_reason || 'Нові результати з’являться після оновлення даних.'}`));
  $('run-story').replaceChildren(story);
  if (rows.length) { const link=el('button','Остання спроба →'); link.onclick=()=>renderDetail(rows.at(-1).id,true); $('run-story').append(link); }
  const resources=[['Виклики моделі','model_calls'],['Вхідні токени','input_tokens'],['Вихідні токени','output_tokens'],['Compute, с','compute_seconds'],['Операції редагування','edit_operations']];
  $('resources').replaceChildren(...resources.map(([label,k])=>{const n=el('div',undefined,'resource'), title=el('div',undefined,'resource-label');title.append(el('span',label),el('span',`${number(line.usage[k])} / ${number(line.limits[k])}`));n.append(title);if(line.limits[k]>0 && line.usage[k]!=null){const p=el('progress');p.max=line.limits[k];p.value=line.usage[k];p.setAttribute('aria-label',label);n.append(p);}return n;}));
  $('chart-caption').textContent=stopNames[line.stop_reason] || (line.stop_reason ? line.stop_reason : 'Запуск ще не має причини зупинки.');
  const info=[['Модель',line.model],['Початкова форма',line.origin],['Середовище',`${data.runtime.engine} · ${data.runtime.cpus ?? '—'} CPU · ${data.runtime.memory_mb ?? '—'} MB`],['Checkpoint',data.snapshot_sha256],['Події',`${rows.filter(a=>a.event_integrity==='verified').length}/${rows.length} спроб перевірено`],['Джерело',data.source]];
  $('context').replaceChildren(...info.flatMap(([k,v])=>[el('dt',k),el('dd',v)]));
  const eventJob = $('event-attempt').value;
  $('event-attempt').replaceChildren(option('','Усі спроби'), ...rows.map(a=>option(a.id,`Спроба ${a.attempt}`)));
  if (rows.some(a=>a.id===eventJob)) $('event-attempt').value=eventJob;
  chart(rows); table($('recent-table'),rows.slice(-4).reverse()); renderAttempts(); renderEvents(); renderVersions(); renderIntegrity(rows); setTab(tab,false);
}
function svg(tag,attrs,text) { const n=document.createElementNS('http://www.w3.org/2000/svg',tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));if(text!==undefined)n.textContent=text;return n; }
function chart(rows) {
  const isCost=$('chart-metric').value==='cost';
  $('chart-title').textContent=isCost?'Накопичена вартість':'Траєкторія якості';
  $('chart-description').textContent=isCost?'Сума записаних витрат спроб · USD':'Частка правильних відповідей · selection suite';
  $('chart-legend').hidden=isCost;
  if(isCost){costChart(rows);return;}
  if(!rows.length || !rows.some(a=>a.baseline!=null||a.quality!=null)){empty($('chart'),'Ще немає виміряної якості');return;}
  const s=svg('svg',{viewBox:'0 0 650 220',role:'img','aria-label':'Якість прийнятого рішення та кандидатів за спробами'});
  const x=i=>48+i*570/Math.max(rows.length,1), y=v=>177-v*151;
  for(const v of [0,.25,.5,.75,1]){s.append(svg('line',{x1:48,y1:y(v),x2:620,y2:y(v),class:'grid-line'}),svg('text',{x:34,y:y(v)+4,'text-anchor':'end',class:'axis-label'},v*100+'%'));}
  const ticks=new Set([0,rows.length]);for(let i=1;i<rows.length;i+=Math.max(1,Math.ceil(rows.length/7)))ticks.add(i);
  for(const i of ticks)s.append(svg('text',{x:x(i),y:204,'text-anchor':'middle',class:'axis-label'},i===0?'Seed':'#'+rows[i-1].attempt));
  let incumbent=rows[0].baseline, path='', last=null;
  for(let i=0;i<=rows.length;i++){
    if(i>0 && rows[i-1].status==='accepted')incumbent=rows[i-1].quality;
    if(incumbent==null){last=null;continue;}
    path+=(last===null?'M':'L')+x(i)+','+y(incumbent)+' ';last=incumbent;
  }
  s.append(svg('path',{d:path,class:'quality-line'}));
  incumbent=rows[0].baseline;
  for(let i=0;i<=rows.length;i++){
    if(i>0 && rows[i-1].status==='accepted')incumbent=rows[i-1].quality;
    if(incumbent!=null)s.append(svg('circle',{cx:x(i),cy:y(incumbent),r:3.5,class:'quality-point'}));
    if(i>0 && rows[i-1].quality!=null){const a=rows[i-1],dot=svg('circle',{cx:x(i),cy:y(a.quality),r:5,class:'candidate-point'});dot.append(svg('title',{},`Спроба ${a.attempt}: ${pct(a.quality)} · ${labels[a.status]}`));s.append(dot);}
  }
  $('chart').replaceChildren(s);
}
function costChart(rows){
  if(!rows.length){empty($('chart'),'Ще немає обліку витрат');return;}
  let cumulative=0;const values=[0];for(const a of rows){cumulative=sum(cumulative,a.spent.cost_microusd);values.push(cumulative);}
  const highest=Math.max(1,...values.filter(v=>v!==null));
  const s=svg('svg',{viewBox:'0 0 650 220',role:'img','aria-label':'Накопичена розрахункова вартість за спробами'}),x=i=>64+i*550/rows.length,y=v=>177-v/highest*151;
  for(const fraction of [0,.5,1]){s.append(svg('line',{x1:64,y1:y(highest*fraction),x2:620,y2:y(highest*fraction),class:'grid-line'}));if(highest>1||fraction===0)s.append(svg('text',{x:55,y:y(highest*fraction)+4,'text-anchor':'end',class:'axis-label'},money(highest*fraction)));}
  let path='';values.forEach((v,i)=>{if(v===null)return;path+=(i===0?'M':'L')+x(i)+','+y(v)+' ';});s.append(svg('path',{d:path,class:'quality-line'}));
  values.forEach((v,i)=>{if(v!==null){const dot=svg('circle',{cx:x(i),cy:y(v),r:4,class:'quality-point'});dot.append(svg('title',{},`Після ${i} спроб: ${money(v)}`));s.append(dot);}if(i===0||i===rows.length||i%Math.max(1,Math.ceil(rows.length/7))===0)s.append(svg('text',{x:x(i),y:204,'text-anchor':'middle',class:'axis-label'},i===0?'Старт':'#'+rows[i-1].attempt));});
  $('chart').replaceChildren(s);
  $('chart-caption').textContent=values.some(v=>v===null)?'Лінія обривається там, де фактична записана витрата невідома. Утримані резерви показані окремо в деталях спроб.':`Разом ${money(cumulative)} за тарифами конфігурації. Це оцінка, не рахунок провайдера.`;
}
function table(target, rows) {
  if(!rows.length){empty(target,'Немає спроб для цього фільтра');return;}
  const t=el('table'),head=el('thead'),hr=el('tr');['СПРОБА','РЕЗУЛЬТАТ','ДО → КАНДИДАТ','ТОКЕНИ','ВАРТІСТЬ','ЗМІНЕНІ ФАЙЛИ'].forEach(h=>hr.append(el('th',h)));head.append(hr);t.append(head);
  const body=el('tbody');rows.forEach(a=>{const r=el('tr'),name=el('td'),b=el('button','#'+String(a.attempt).padStart(2,'0')+' ↗');b.setAttribute('aria-label',`Відкрити спробу ${a.attempt}`);b.onclick=()=>renderDetail(a.id,true);name.append(b);const state=el('td');state.append(badge(a.status));r.append(name,state,el('td',`${pct(a.baseline)} → ${pct(a.quality)}`,'mono'),el('td',number(sum(a.spent.input_tokens,a.spent.output_tokens)),'mono'),el('td',money(a.spent.cost_microusd),'mono'),el('td',number(a.net_changed_files),'mono'));body.append(r);});t.append(body);target.replaceChildren(t);
}
function renderAttempts() {
  const filter = $('status-filter').value, query = $('attempt-search').value.trim().toLocaleLowerCase();
  const rows = scoped().filter(a => (!filter || a.status === filter) &&
    [`#${a.attempt}`, a.id, a.reason, labels[a.status]].join(' ').toLocaleLowerCase().includes(query));
  if ($('attempt-order').value !== 'oldest') rows.reverse();
  table($('attempt-table'), rows);
  $('attempt-summary').textContent = `${rows.length} з ${scoped().length} спроб`;
  $('reset-attempts').disabled = !filter && !query && $('attempt-order').value === 'newest';
}
function renderEvents(){
  const query=$('event-search').value.trim().toLocaleLowerCase(), rows=scoped();
  const job=$('event-attempt').value, type=$('event-type').value;
  const category=e=>e.event_type.startsWith('provider_')?'provider':e.event_type.startsWith('tool_')?'tool':e.event_type.startsWith('budget_')?'budget':'other';
  const all=rows.flatMap(a=>a.events.map(e=>({...e,job:a.id,attempt:a.attempt,integrity:a.event_integrity}))).filter(e=>(!job||e.job===job)&&(!type||category(e)===type)&&(JSON.stringify(e)+' '+(eventNames[e.event_type]||'')).toLocaleLowerCase().includes(query));
  const total=rows.reduce((n,a)=>n+a.events.length,0);
  $('event-summary').textContent=`Знайдено ${all.length} із ${total} подій · показано ${Math.min(eventLimit,all.length)}. ${rows.some(a=>a.event_integrity==='error')?'Є спроби з помилкою перевірки — дивіться «Контекст і докази».':''}`;
  $('reset-events').disabled=!query&&!job&&!type;
  const expanded=new Set([...$('event-list').querySelectorAll('details[open]')].map(d=>d.dataset.event));
  const visible=all.slice(0,eventLimit);
  $('event-list').replaceChildren(...visible.map(e=>{const d=el('details',undefined,'event'),s=el('summary');d.dataset.event=e.job+':'+e.event_id;const date=new Date(e.timestamp_utc);s.append(el('time',Number.isNaN(date.getTime())?'—':date.toLocaleTimeString('uk-UA')),el('span',(eventNames[e.event_type]||e.event_type)+(e.payload.name?' · '+String(e.payload.name):'')),el('span',`#${e.attempt}`,'event-job'));d.append(s);d.addEventListener('toggle',()=>{if(d.open&&!d.querySelector('pre'))d.append(el('pre',JSON.stringify(e.payload,null,2)));});if(expanded.has(d.dataset.event))d.open=true;return d;}));
  if(!visible.length)empty($('event-list'),'Подій за цим запитом немає');$('more-events').hidden=all.length<=eventLimit;
}
function versionLabel(v) { return v.attempt === 0 ? 'Початкова версія · Seed' : `Спроба ${v.attempt} · ${labels[data.attempts.find(a=>a.id===v.id)?.status] || v.label}`; }
function renderVersions(){const versions=data.versions.filter(v=>v.lineage===activeLineage().id);for(const id of ['version-before','version-after']){const prev=$(id).value;$(id).replaceChildren(...versions.map(v=>option(v.id,versionLabel(v))));if(versions.some(v=>v.id===prev))$(id).value=prev;else if(id==='version-after'&&versions.length)$(id).value=versions.at(-1).id;}showVersions();}
function paintDiff(target,text){if(text===null||text===undefined){target.textContent='Порівняння недоступне: бракує перевірених знімків.';return;}if(text===''){target.textContent='Файли ідентичні. Змін немає.';return;}target.replaceChildren(...text.split('\n').map(line=>el('span',line,line.startsWith('+')&&!line.startsWith('+++')?'add':line.startsWith('-')&&!line.startsWith('---')?'remove':'')));}
function showVersions(){const before=data.versions.find(v=>v.id===$('version-before').value&&v.lineage===activeLineage().id),after=data.versions.find(v=>v.id===$('version-after').value&&v.lineage===activeLineage().id);$('before-code').textContent=before?.text??'Код недоступний';$('after-code').textContent=after?.text??'Код недоступний';$('before-title').textContent=before?versionLabel(before):'До';$('after-title').textContent=after?versionLabel(after):'Після';$('version-note').textContent=before&&after?`До: ${before.sha256.slice(0,12)} · Після: ${after.sha256.slice(0,12)} · ${before.sha256===after.sha256?'Тексти ідентичні':'Тексти відрізняються'}. Артефакт «після»: ${labels[after.integrity]}.`:'Немає знімків для порівняння.';$('swap-versions').disabled=!before||!after;paintDiff($('version-diff'),comparisonDiff(before,after));}
function comparisonDiff(before,after){
  if(!before||!after)return null;
  if(before.text==null||after.text==null)return null;
  if(before.text===after.text)return '';
  // One bounded replacement block, preserving exact lines; no similarity score.
  const a=before.text.split('\n'),b=after.text.split('\n');let first=0,endA=a.length,endB=b.length;
  while(first<endA&&first<endB&&a[first]===b[first])first++;
  while(endA>first&&endB>first&&a[endA-1]===b[endB-1]){endA--;endB--;}
  return [`--- ${before.label}`,`+++ ${after.label}`,`@@ рядок ${first+1} · ${endA-first} вилучено / ${endB-first} додано @@`,...a.slice(Math.max(0,first-3),first).map(x=>' '+x),...a.slice(first,endA).map(x=>'-'+x),...b.slice(first,endB).map(x=>'+'+x),...b.slice(endB,endB+3).map(x=>' '+x)].join('\n');
}
function noteKey(id){return `prism.review.v1:${data.id}:${id}`;}
function readNote(id){try{return JSON.parse(localStorage.getItem(noteKey(id))||'null');}catch{return null;}}
function renderDetail(id, open, write = true) {
  const a = scoped().find(a => a.id === id);
  if (!a) return;
  selectedAttempt = id;
  $('detail-title').textContent = `Спроба ${a.attempt} · ${a.lineage}`;
  const rows = scoped(), position = rows.findIndex(a => a.id === id);
  $('detail-position').textContent = `${position+1} із ${rows.length}`;
  $('previous-attempt').disabled = position === 0;
  $('next-attempt').disabled = position === rows.length-1;
  $('detail-code').disabled = !data.versions.some(v => v.id === id && v.lineage === a.lineage);
  const body = $('detail-body');
  body.replaceChildren(badge(a.status), el('p', a.reason || 'Причина не записана.'));
  const metrics = el('div', undefined, 'detail-metrics');
  [['До',pct(a.baseline)],['Кандидат',pct(a.quality)],['Вартість',money(a.spent.cost_microusd)],['Події',labels[a.event_integrity]],['Артефакт',labels[a.artifact_integrity]],['Compute, с',number(a.spent.compute_seconds)]].forEach(([k,v]) => {
    const n = el('div', k); n.append(el('strong', v)); metrics.append(n);
  });
  body.append(metrics);
  if (a.reservation) body.append(el('p', `Утриманий резерв спроби: ${money(a.reservation.cost_microusd)}. Фактична витрата може бути невідома.`, 'notice'));
  body.append(el('h3', 'Результати оцінювання'));
  const evaluations = el('dl');
  const e = a.evaluation || {};
  for (const [title, value] of [['Правильні відповіді',`${number(e.correct)} / ${number(e.cases)}`],['Час оцінювання',e.duration_ms == null ? 'Не виміряно' : `${number(e.duration_ms)} мс`],['Тайм-аути',number(e.timed_out_cases)],['Помилки виконання',number(e.execution_failures)]]) evaluations.append(el('dt',title),el('dd',value));
  body.append(evaluations);
  const raw = el('details'); raw.append(el('summary', 'Усі записані показники'), el('pre', JSON.stringify(a.evaluation,null,2))); body.append(raw);
  body.append(el('h3', 'Зміни відносно прийнятої версії'));
  const diff = el('pre', undefined, 'diff'); paintDiff(diff,a.diff); body.append(diff);
  if (open) {
    const saved = readNote(id); $('note').value = saved?.text || '';
    $('note-status').textContent = saved ? 'Збережена локальна нотатка' : '';
    if (!$('detail').open) $('detail').showModal();
    $('detail').scrollTop = 0;
    if (write) saveRoute();
  }
}
function renderIntegrity(rows) {
  if (!rows.length) { empty($('integrity-table'), 'Немає спроб для перевірки'); return; }
  const t=el('table'), head=el('thead'), header=el('tr'), body=el('tbody');
  ['СПРОБА','РЕЗУЛЬТАТ','ЛАНЦЮЖОК ПОДІЙ','АРТЕФАКТ'].forEach(x=>header.append(el('th',x)));
  head.append(header); t.append(head);
  rows.forEach(a=>{const r=el('tr'), cell=el('td'), b=el('button',`Спроба ${a.attempt} ↗`);b.onclick=()=>renderDetail(a.id,true);cell.append(b);r.append(cell);[a.status,a.event_integrity,a.artifact_integrity].forEach(v=>{const c=el('td');c.append(badge(v));r.append(c);});body.append(r);});
  t.append(body); $('integrity-table').replaceChildren(t);
}
function download(){if(!data)return;const notes=data.attempts.map(a=>({attempt_id:a.id,...(readNote(a.id)||{})})).filter(n=>n.text);const body=JSON.stringify({exported_at:new Date().toISOString(),run:data,researcher_notes:notes},null,2);const url=URL.createObjectURL(new Blob([body],{type:'application/json'}));const a=el('a');a.href=url;a.download='prism-'+data.id+'.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function closeDetail(write = true) {
  selectedAttempt = null;
  if ($('detail').open) $('detail').close();
  if (write) saveRoute();
}
function resetFilters() {
  for (const id of ['attempt-search','status-filter','event-search','event-attempt','event-type']) $(id).value='';
  $('attempt-order').value='newest'; eventLimit=100;
}
const mobile = matchMedia('(max-width:700px)');
function setMenu(open) {
  const show = mobile.matches && open;
  document.body.classList.toggle('nav-open',show);
  $('nav-overlay').hidden=!show;
  $('open-menu').setAttribute('aria-expanded',String(show));
  $('sidebar').inert=mobile.matches&&!show;
  $('main-content').inert=show;
  if (show) $('close-menu').focus();
  else if (mobile.matches && $('sidebar').contains(document.activeElement)) $('open-menu').focus();
}
function applyTheme(theme) {
  document.documentElement.dataset.theme=theme==='dark'?'dark':'light';
  $('theme-toggle').setAttribute('aria-label',theme==='dark'?'Увімкнути світлу тему':'Увімкнути темну тему');
  $('theme-toggle').title=theme==='dark'?'Світла тема':'Темна тема';
}
try { applyTheme(localStorage.getItem('prism.theme')); } catch { applyTheme('light'); }
$('theme-toggle').onclick=()=>{const theme=document.documentElement.dataset.theme==='dark'?'light':'dark';applyTheme(theme);try{localStorage.setItem('prism.theme',theme);}catch{/* Theme remains usable without storage. */}};
$('open-menu').onclick=()=>setMenu(true);
for(const id of ['close-menu','nav-overlay']) $(id).onclick=()=>setMenu(false);
mobile.addEventListener('change',()=>setMenu(false)); setMenu(false);
for(const id of ['help','footer-help']) $(id).onclick=()=>{setMenu(false);$('help-dialog').showModal();};
$('close-help').onclick=()=>$('help-dialog').close();
document.addEventListener('keydown',event=>{
  if(event.key==='Escape'&&document.body.classList.contains('nav-open')){setMenu(false);return;}
  if(event.ctrlKey||event.altKey||event.metaKey||event.target.closest('input,textarea,select,[contenteditable=true]')||$('detail').open||$('help-dialog').open)return;
  if(event.key==='?'){event.preventDefault();setMenu(false);$('help-dialog').showModal();}
  if(event.key==='/'){event.preventDefault();const id=tab==='attempts'?'attempt-search':tab==='events'?'event-search':'run-search';if(id==='run-search'&&mobile.matches)setMenu(true);$(id).focus();}
});
$('refresh').onclick=()=>refresh(); $('export').onclick=download;
document.querySelector('.skip-link').onclick=event=>{event.preventDefault();$('main-content').focus();};
$('run-search').oninput=renderRuns;
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>setTab(b.dataset.tab));
$('all-attempts').onclick=()=>setTab('attempts');
$('lineage').onchange=()=>{closeDetail(false);resetFilters();render();saveRoute();};
for(const id of ['attempt-search','status-filter','attempt-order']) $(id)[id==='attempt-search'?'oninput':'onchange']=()=>{renderAttempts();saveRoute(true);};
$('reset-attempts').onclick=()=>{$('attempt-search').value='';$('status-filter').value='';$('attempt-order').value='newest';renderAttempts();saveRoute(true);};
$('chart-metric').onchange=()=>{if(data){render();saveRoute(true);}};
for(const id of ['event-search','event-attempt','event-type']) $(id)[id==='event-search'?'oninput':'onchange']=()=>{eventLimit=100;renderEvents();saveRoute(true);};
$('reset-events').onclick=()=>{for(const id of ['event-search','event-attempt','event-type'])$(id).value='';eventLimit=100;renderEvents();saveRoute(true);};
$('more-events').onclick=()=>{eventLimit+=100;renderEvents();};
for(const id of ['version-before','version-after']) $(id).onchange=()=>{showVersions();saveRoute(true);};
$('swap-versions').onclick=()=>{const before=$('version-before').value;$('version-before').value=$('version-after').value;$('version-after').value=before;showVersions();saveRoute(true);};
$('close-detail').onclick=()=>closeDetail();
$('detail').addEventListener('cancel',event=>{event.preventDefault();closeDetail();});
for(const [id,offset] of [['previous-attempt',-1],['next-attempt',1]]) $(id).onclick=()=>{const rows=scoped(),index=rows.findIndex(a=>a.id===selectedAttempt);if(rows[index+offset])renderDetail(rows[index+offset].id,true);};
$('detail-events').onclick=()=>{const id=selectedAttempt;closeDetail(false);$('event-attempt').value=id;$('event-search').value='';$('event-type').value='';eventLimit=100;renderEvents();setTab('events');};
$('detail-code').onclick=()=>{
  const id=selectedAttempt, rows=scoped(), index=rows.findIndex(a=>a.id===id);
  const previous=rows.slice(0,index).filter(a=>a.status==='accepted').at(-1);
  const seed=data.versions.find(v=>v.lineage===activeLineage().id&&v.attempt===0);
  closeDetail(false); $('version-before').value=previous?.id||seed?.id||''; $('version-after').value=id;
  showVersions();setTab('versions');
};
$('note').oninput=()=>{if(!selectedAttempt||!data)return;try{localStorage.setItem(noteKey(selectedAttempt),JSON.stringify({text:$('note').value,snapshot_sha256:data.snapshot_sha256,updated_at:new Date().toISOString()}));$('note-status').textContent='Збережено в цьому браузері';}catch{$('note-status').textContent='Не вдалося зберегти. Скопіюйте нотатку перед закриттям.';}};
window.addEventListener('popstate',()=>{if(runs.length)applyLocation();});
setInterval(()=>{if($('auto').checked&&!$('refresh').disabled)refresh();},5000);
(async()=>{try{runs=await getJSON('/api/runs');if(runs.length)await applyLocation();else throw new Error('Не зареєстровано жодного запуску.');}catch(e){$('error').textContent=e.message;$('error').hidden=false;}})();
