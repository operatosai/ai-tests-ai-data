// usage: node playtest.js <game.html> <outdir> [--video]
const {chromium}=require('playwright-core');
const fs=require('fs'),path=require('path');
const [,, file, out, ...flags]=process.argv; fs.mkdirSync(out,{recursive:true});
function rng(s){return()=>{s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const KEYS=['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','a','d','w','s','Space','Space'];
async function open(browser,video){
  const ctx=await browser.newContext({viewport:{width:1280,height:720},...(video?{recordVideo:{dir:path.join(out,'video'),size:{width:1280,height:720}}}:{})});
  const page=await ctx.newPage(); const errs=[];
  page.on('console',m=>{if(m.type()==='error')errs.push('console: '+m.text().slice(0,300))});
  page.on('pageerror',e=>errs.push('pageerror: '+String(e.message).slice(0,300)));
  page.on('dialog',d=>d.dismiss().catch(()=>{}));
  return {ctx,page,errs};
}
const gs=p=>p.evaluate(()=>{try{const g=window.gameState;return g&&typeof g==='object'?{score:g.score,state:g.state}:null}catch(e){return null}}).catch(()=>null);
async function start(p){
  for(let i=0;i<8;i++){const s=await gs(p); if(s&&s.state==='playing')return true;
    await p.keyboard.press(['Enter','Space','Enter','Space'][i%4]).catch(()=>{}); await p.mouse.click(640,360).catch(()=>{}); await sleep(400);}
  const s=await gs(p); return !!(s&&s.state==='playing');
}
(async()=>{
  const R={file,time:new Date().toISOString(),points:{},notes:[]};
  const browser=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
  // ---- phase A: bot
  const A=await open(browser,flags.includes('--video')); const p=A.page; const t0=Date.now();
  let loaded=true;
  try{await p.goto('file://'+path.resolve(file),{waitUntil:'load',timeout:5000})}catch(e){loaded=false;R.notes.push('load: '+e.message.slice(0,150))}
  await sleep(1200);
  R.points.P1_loads=loaded&&!A.errs.some(e=>e.startsWith('pageerror'))?1:0;
  const hook0=await gs(p);
  R.hook_at_load=hook0;
  R.points.P8_hook=hook0&&typeof hook0.score==='number'&&['menu','playing','over','won'].includes(hook0.state)?1:0;
  const blank=await p.evaluate(()=>{const c=document.querySelector('canvas');return {canvas:!!c,w:c?c.width:0,h:c?c.height:0,text:document.body.innerText.length,nodes:document.querySelectorAll('*').length}}).catch(()=>({}));
  R.dom=blank;
  await p.screenshot({path:path.join(out,'menu.png')}).catch(()=>{});
  const shot0=await p.screenshot().catch(()=>null);
  R.points.P3_renders=shot0&&shot0.length>6000?1:0; R.menu_png_bytes=shot0?shot0.length:0;
  R.rAF_5s=await p.evaluate(()=>new Promise(r=>{let n=0;const t=performance.now();function f(){n++;if(performance.now()-t<2000)requestAnimationFrame(f);else r(n/2*5)}requestAnimationFrame(f)})).catch(()=>-1);
  const started=await start(p); R.started=started;
  const rnd=rng(12345); let scores=new Set(),states=new Set(),diffs=0,prev=null,lastScore=null,sawOver=false,sawWon=false,maxScore=0,frames=0,restartOK=0,overAt=null;
  const BOT_MS=60000, bot0=Date.now(); let nextShot=0, shotIdx=0; const sampleTimes=[];
  while(Date.now()-bot0<BOT_MS){
    const el=Date.now()-bot0;
    if(el>=nextShot){ const b=await p.screenshot({path:path.join(out,`f${String(shotIdx).padStart(2,'0')}.png`)}).catch(()=>null); shotIdx++; nextShot+=7500; if(b&&prev&&Buffer.compare(b,prev)!==0)diffs++; if(b)prev=b; }
    const s=await gs(p);
    if(s){states.add(s.state); if(typeof s.score==='number'){scores.add(s.score); maxScore=Math.max(maxScore,s.score)}
      if(s.state==='won')sawWon=true;
      if(s.state==='over'&&!sawOver){sawOver=true;overAt=el;await p.screenshot({path:path.join(out,'over.png')}).catch(()=>{});
        const before=s.score; for(let i=0;i<6;i++){await p.keyboard.press(['Enter','Space','Enter','Space','r','Enter'][i]).catch(()=>{});await p.mouse.click(640,360).catch(()=>{});await sleep(500);const t=await gs(p);if(t&&t.state==='playing'){restartOK=(t.score<=before||t.score===0)?1:0.5;break}}}
      else if(s.state!=='playing'){await p.keyboard.press('Enter').catch(()=>{});await p.keyboard.press('Space').catch(()=>{});await p.mouse.click(640,360).catch(()=>{})}
    }
    const r=rnd();
    if(r<0.2){await p.mouse.move(100+rnd()*1080,100+rnd()*520).catch(()=>{}); if(rnd()<0.3)await p.mouse.down().then(()=>sleep(80)).then(()=>p.mouse.up()).catch(()=>{})}
    else{const k=KEYS[Math.floor(rnd()*KEYS.length)]; await p.keyboard.down(k).catch(()=>{}); await sleep(120+rnd()*300); await p.keyboard.up(k).catch(()=>{})}
    await sleep(30);
  }
  await p.screenshot({path:path.join(out,'end.png')}).catch(()=>{});
  R.points.P2_no_console_errors=A.errs.length===0?1:0;
  R.points.P4_input_changes_screen=diffs>=3?1:0;
  R.points.P5_score_changes=scores.size>=2?1:0;
  R.points.P7_restart_works=restartOK===1?1:(restartOK?0.5:0);
  R.bot={states:[...states],distinct_scores:scores.size,max_score:maxScore,saw_over:sawOver,over_at_s:overAt&&overAt/1000,saw_won:sawWon,started,screen_changes:diffs};
  R.errors=[...new Set(A.errs)].slice(0,12); R.error_count=A.errs.length;
  await A.ctx.close();
  // ---- phase B: idle
  let idleOver=false, idleState=null;
  if(!sawOver){
    const B=await open(browser,false);
    try{await B.page.goto('file://'+path.resolve(file),{timeout:5000});await sleep(800);
      if(await start(B.page)){ const t=Date.now(); while(Date.now()-t<45000){const s=await gs(B.page); if(s&&s.state==='over'){idleOver=true;break} await sleep(500)} idleState=await gs(B.page)}}catch(e){}
    await B.ctx.close();
  }
  R.idle={over:idleOver,final:idleState};
  R.points.P6_can_lose=(sawOver||idleOver)?1:0;
  R.total=Object.values(R.points).reduce((a,b)=>a+b,0);
  const bytes=fs.statSync(file).size; R.bytes=bytes; R.lines=fs.readFileSync(file,'utf8').split('\n').length;
  R.seconds=(Date.now()-t0)/1000;
  // video rename
  if(flags.includes('--video')){try{const d=path.join(out,'video');const f=fs.readdirSync(d).find(x=>x.endsWith('.webm'));if(f)fs.renameSync(path.join(d,f),path.join(out,'play.webm'));fs.rmSync(d,{recursive:true,force:true})}catch(e){}}
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(R,null,1));
  await browser.close(); console.log(JSON.stringify({total:R.total,points:R.points,bot:R.bot,errs:R.error_count}));
})().catch(e=>{console.log('FATAL',e.message);process.exit(2)});
