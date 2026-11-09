const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {JSDOM, VirtualConsole} = require('jsdom');
const root = path.join(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const urban = read('urban.js'), guide = read('guide-navigation.js');
const topics = {facilities:'services.html#nightcare-photo',fees:'fees.html#house-fees',process:'process.html',faq:'faq.html'};
const tick = () => new Promise(resolve => setTimeout(resolve, 30));

function fixture(file='guide-en.html', hash='#fees', options={}) {
  const errors = [], warnings = [], scrolls = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', error => errors.push(error));
  virtualConsole.on('warn', warning => warnings.push(warning));
  const dom = new JSDOM(read(file), {url:'https://lumirize.co/'+file+hash,runScripts:'outside-only',pretendToBeVisual:true,virtualConsole});
  const w = dom.window, d = w.document, menu = d.getElementById('mobileMenu');
  w.scrollTo = (...args) => scrolls.push(args);
  Object.defineProperty(w,'scrollY',{value:850,configurable:true});
  w.matchMedia = query => ({matches:options.reduced && query.includes('reduced-motion')});
  w.HTMLElement.prototype.scrollIntoView = function () { this.scrolledIntoView = true; };
  w.HTMLElement.prototype.getClientRects = function () {return this.hidden || this.closest('[hidden]') ? [] : [{width:44,height:44}];};
  if(options.legacy) {
    w.Object.hasOwn = undefined;
    delete w.HTMLDialogElement.prototype.open;
    if(options.noScrollOptions) Object.defineProperty(d.documentElement,'style',{value:{},configurable:true});
  } else {
    menu.showModal = () => {if(options.showThrows) throw Error('show failed'); menu.setAttribute('open','');};
    menu.close = () => {if(options.closeThrows) throw Error('close failed'); menu.removeAttribute('open'); menu.dispatchEvent(new w.Event('close'));};
  }
  if(options.animationThrows) menu.animate = () => {throw Error('animation unavailable');};
  if(options.before) options.before(w);
  w.eval(urban);
  if(d.body.classList.contains('guide-page')) w.eval(guide);
  return {dom,w,d,menu,errors,warnings,scrolls,cleanup:()=>w.close()};
}
function assertUnlocked(f) {
  assert.equal(f.d.body.classList.contains('menu-open'),false);
  assert.equal(f.d.documentElement.classList.contains('menu-open'),false);
  assert.equal(f.d.body.style.getPropertyValue('--menu-scroll-offset'),'');
  assert.equal(f.d.querySelector('.menu-toggle').getAttribute('aria-expanded'),'false');
  assert.equal(f.menu.hasAttribute('open'),false);
  assert.equal(f.d.activeElement,f.d.querySelector('.menu-toggle'));
}
function assertLinks(f,topic) {
  for(const scope of ['.home-languages','.menu-languages']) {
    assert.equal(f.d.querySelector(scope+' a[lang="ja"]').getAttribute('href'),topics[topic]);
    for(const lang of ['en','ko','tl','th']) assert.equal(f.d.querySelector(scope+' a[lang="'+lang+'"]').getAttribute('href'),'guide-'+lang+'.html#'+topic);
  }
}

for(const legacy of [false,true]) for(const lang of ['en','ko','tl','th']) for(const topic of Object.keys(topics)) {
  test(`${legacy?'fallback':'native'} ${lang}/${topic}: top, menu, language targets, restored page`, async () => {
    const f=fixture(`guide-${lang}.html`,'#'+topic,{legacy,noScrollOptions:legacy});
    const historyLength=f.w.history.length;
    f.d.querySelector('footer a[href="#top"]').click();
    assert.equal(f.w.location.hash,'#'+topic);assert.equal(f.w.history.length,historyLength);assertLinks(f,topic);
    if(legacy) assert.deepEqual(f.scrolls.at(-1),[0,0]); else assert.equal(f.scrolls.at(-1)[0].behavior,'smooth');
    f.d.querySelector('.menu-toggle').click();
    assert.equal(f.menu.hasAttribute('open'),true);assert.equal(f.d.activeElement,f.d.querySelector('.menu-close'));
    assert.equal(f.d.body.classList.contains('menu-open'),true);assertLinks(f,topic);
    if(legacy) {
      assert.equal(f.menu.getAttribute('role'),'dialog');assert.equal(f.menu.getAttribute('aria-modal'),'true');
      assert.equal(f.d.querySelector('main').getAttribute('aria-hidden'),'true');
      assert.equal(f.d.querySelector('.menu-fallback-backdrop').hidden,false);
    } else assert.equal(f.d.querySelector('.menu-fallback-backdrop'),null);
    f.d.querySelector('.menu-close').click();await tick();assertUnlocked(f);
    if(legacy) {assert.equal(f.d.querySelector('main').hasAttribute('aria-hidden'),false);assert.equal(f.d.querySelector('.menu-fallback-backdrop').hidden,true);}
    assert.deepEqual(f.scrolls.at(-1),[0,850]);
    f.w.dispatchEvent(new f.w.PageTransitionEvent('pageshow',{persisted:true}));assertLinks(f,topic);
    assert.equal(f.errors.length,0);f.cleanup();
  });
}

for(const file of fs.readdirSync(root).filter(name=>name.endsWith('.html')&&read(name).includes('id="mobileMenu"'))) {
  test(`${file}: fallback menu opens, Escape closes and focus returns`,async()=>{
    const f=fixture(file,'',{legacy:true});
    assert.equal(f.menu.parentElement,f.d.body);
    f.d.querySelector('.menu-toggle').click();assert.equal(f.menu.hasAttribute('open'),true);
    f.d.dispatchEvent(new f.w.KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));
    await tick();assertUnlocked(f);assert.equal(f.errors.length,0);f.cleanup();
  });
}

test('fallback traps keyboard focus, blocks background focus, closes on backdrop and preserves existing aria-hidden',async()=>{
  const f=fixture('guide-en.html','#fees',{legacy:true,before:w=>w.document.querySelector('main').setAttribute('aria-hidden','false')});
  const toggle=f.d.querySelector('.menu-toggle'),close=f.d.querySelector('.menu-close');
  toggle.click();const links=f.menu.querySelectorAll('a[href]');const last=links[links.length-1];
  close.focus();const backwards=new f.w.KeyboardEvent('keydown',{key:'Tab',shiftKey:true,bubbles:true,cancelable:true});close.dispatchEvent(backwards);
  assert.equal(backwards.defaultPrevented,true);assert.equal(f.d.activeElement,last);
  const forwards=new f.w.KeyboardEvent('keydown',{key:'Tab',bubbles:true,cancelable:true});last.dispatchEvent(forwards);
  assert.equal(forwards.defaultPrevented,true);assert.equal(f.d.activeElement,close);
  f.d.querySelector('main a').focus();assert.equal(f.d.activeElement,close);
  f.d.querySelector('.menu-fallback-backdrop').click();await tick();assertUnlocked(f);
  assert.equal(f.d.querySelector('main').getAttribute('aria-hidden'),'false');assert.equal(f.errors.length,0);f.cleanup();
});

for(const legacy of [false,true]) {
  test(`${legacy?'fallback':'native'} menu anchors preserve topic, close and focus target`,async()=>{
    const f=fixture('guide-en.html','#facilities',{legacy});
    f.d.querySelector('.menu-toggle').click();f.d.querySelector('#mobileMenu a[href="guide-en.html#fees"]:not([lang])').click();
    await tick();assert.equal(f.w.location.hash,'#fees');assertLinks(f,'fees');
    assert.equal(f.menu.hasAttribute('open'),false);assert.equal(f.d.body.classList.contains('menu-open'),false);
    assert.equal(f.d.activeElement,f.d.getElementById('fees'));assert.equal(f.d.getElementById('fees').scrolledIntoView,true);
    assert.equal(f.errors.length,0);f.cleanup();
  });
  test(`${legacy?'fallback':'native'} pageshow closes a restored open menu`,async()=>{
    const f=fixture('guide-en.html','#faq',{legacy});f.d.querySelector('.menu-toggle').click();
    f.w.dispatchEvent(new f.w.PageTransitionEvent('pageshow',{persisted:true}));await tick();
    assertUnlocked(f);assertLinks(f,'faq');assert.equal(f.errors.length,0);f.cleanup();
  });
  test(`${legacy?'fallback':'native'} ordinary topic navigation and back/forward`,async()=>{
    const f=fixture('guide-en.html','#fees',{legacy});f.d.querySelector('main a[href="#process"]').click();await tick();
    assert.equal(f.w.location.hash,'#process');assertLinks(f,'process');
    f.w.history.back();await tick();assert.equal(f.w.location.hash,'#fees');assertLinks(f,'fees');
    f.w.history.forward();await tick();assert.equal(f.w.location.hash,'#process');assertLinks(f,'process');f.cleanup();
  });
}

for(const options of [{showThrows:true},{closeThrows:true},{animationThrows:true},{legacy:true,animationThrows:true},{legacy:true,reduced:true}]) {
  test(`menu error/reduced-motion recovery ${JSON.stringify(options)}`,async()=>{
    const f=fixture('guide-en.html','#fees',options);f.d.querySelector('.menu-toggle').click();
    if(!options.showThrows) f.d.querySelector('.menu-close').click();await tick();assertUnlocked(f);
    assert.equal(f.errors.length,0);f.cleanup();
  });
}

test('native canceled close animation still releases scroll lock',async()=>{
  const f=fixture('guide-en.html','#fees');f.d.querySelector('.menu-toggle').click();
  f.menu.animate=()=>({finished:Promise.reject(Error('canceled'))});f.d.querySelector('.menu-close').click();await tick();
  assertUnlocked(f);assert.equal(f.errors.length,0);f.cleanup();
});
test('contact language preselection works without Object.hasOwn',()=>{
  const f=fixture('contact.html','?lang=ko#languages',{legacy:true});
  assert.equal(f.d.getElementById('language').value,'한국어');assert.equal(f.errors.length,0);f.cleanup();
});
test('modified back-to-top clicks retain browser behavior',()=>{
  for(const modifier of ['ctrlKey','metaKey','shiftKey','altKey']) {
    const f=fixture('guide-en.html','#faq',{legacy:true});const event=new f.w.MouseEvent('click',{bubbles:true,cancelable:true,[modifier]:true});
    f.d.querySelector('footer a[href="#top"]').dispatchEvent(event);assert.equal(event.defaultPrevented,false);assertLinks(f,'faq');f.cleanup();
  }
});
test('reduced motion and pre-existing header tabindex are preserved',()=>{
  const f=fixture('guide-en.html','#faq',{reduced:true,before:w=>w.document.getElementById('top').setAttribute('tabindex','0')});
  f.d.querySelector('footer a[href="#top"]').click();assert.equal(f.scrolls.at(-1)[0].behavior,'instant');
  f.d.querySelector('.home-languages a').focus();assert.equal(f.d.getElementById('top').getAttribute('tabindex'),'0');f.cleanup();
});
test('every menu page loads the versioned navigation and compatibility styles',()=>{
  let pages=0;
  for(const name of fs.readdirSync(root).filter(name=>name.endsWith('.html'))) {
    const html=read(name);
    if(!html.includes('id="mobileMenu"')) continue;
    assert.match(html,/urban\.js\?v=20261109-safari/);
    assert.match(html,/site-improvements\.css\?v=20261109-safari/);
    if(name.startsWith('guide-')) assert.match(html,/guide-navigation\.js\?v=20261109-safari/);
    pages++;
  }
  assert.equal(pages,23);
});
