import {translations} from './contact-translations.mjs?v=20261103-audit';
const names = {ja:'日本語', en:'English', ko:'한국어', tl:'Tagalog', th:'ภาษาไทย'};
const language = document.getElementById('language');
const requested = new URLSearchParams(location.search).get('lang');
if (language && Object.hasOwn(names, requested)) language.value = names[requested];
const current = () => Object.keys(names).find(key => names[key] === language?.value) || 'ja';
export const contactText = (key, original) => translations[current()]?.[key] ?? original;
const originals = new Map();
function text(element, value) {
  if (!element) return;
  if (!originals.has(element)) originals.set(element, element.textContent);
  element.textContent = value ?? originals.get(element);
}
const fields = ['name','contact-method','voicemail-permission','contact-time','contact-time-details','email','phone','topic','language','message'];
const bindings = {'contact-form-title':'title','contact-form-intro':'intro','contact-preferences-title':'group','contact-preferences-hint':'groupHint','voicemail-hint':'voicemailHint','contact-time-hint':'timeHint','message-hint':'messageHint','privacy-agreement':'privacy','privacy-link':'privacyLink','email-fallback':'fallback','email-fallback-note':'fallbackNote','form-service-text':'service','form-service-link':'serviceLink'};
const initialPlaceholder = document.getElementById('contact-time-details')?.placeholder;
export function localizeContactForm() {
  const lang = current(), data = translations[lang];
  document.getElementById('contact-form')?.setAttribute('lang',lang === 'tl' ? 'fil' : lang);
  for (const [id,key] of Object.entries(bindings)) text(document.getElementById(id),data?.[key]);
  fields.forEach((id,i) => {
    const label = document.querySelector('label[for="'+id+'"]');
    if (!label) return;
    let node = Array.from(label.childNodes).find(n => n.nodeType === 3 && n.textContent.trim());
    if (node) { if (!originals.has(node)) originals.set(node,node.textContent); node.textContent = data ? data.labels[i]+' ' : originals.get(node); }
    const badge = label.querySelector('span');
    if (badge && !badge.id) text(badge,data ? (document.getElementById(id).required ? data.required : data.optional) : undefined);
  });
  for (const [id,key] of [['contact-method','methods'],['voicemail-permission','voicemail'],['contact-time','times'],['topic','topics']]) {
    Array.from(document.getElementById(id).options).forEach((option,i) => text(option,data?.[key]?.[i]));
  }
  const timing = document.getElementById('contact-time-details');
  if (timing) timing.placeholder = data?.placeholder ?? initialPlaceholder;
  text(document.querySelector('#contact-form button[type="submit"]'),data?.send);
  if (language) {
    text(language.options[0],data?.methods[0]);
    text(language.options[6],data?.topics[6]);
  }
}
