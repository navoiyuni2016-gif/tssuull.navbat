'use strict';
function uzbekAlphabet(value){return String(value).replace(/([oOgG])['‘’ʻʼ`]/g,(_,letter)=>({o:'ö',O:'Ö',g:'ğ',G:'Ğ'}[letter])).replace(/sh|ch/gi,match=>{const letter=match.toLowerCase()==='sh'?'ş':'ç';return match[0]===match[0].toUpperCase()?letter.toUpperCase():letter})}
// Apply to visible language only: URLs, form values, login identifiers and code stay intact.
if(typeof document!=='undefined'){
  function translate(root){
    const context=root.nodeType===3?root.parentElement:root;
    if(context&&(context.closest('script,style,code,pre,.technical')||context.closest('[lang]')?.getAttribute('lang')!=='uz'))return;
    if(root.nodeType===3){const p=root.parentElement;if(p&&!p.closest('script,style,code,pre,.technical')){const value=uzbekAlphabet(root.data);if(value!==root.data)root.data=value;}return;}
    if(root.nodeType!==1)return;
    if(root.matches('script,style,code,pre,.technical'))return;
    for(const attr of ['placeholder','title','aria-label','alt'])if(root.hasAttribute(attr)){const old=root.getAttribute(attr),value=uzbekAlphabet(old);if(old!==value)root.setAttribute(attr,value);}
    for(const child of root.childNodes)translate(child);
  }
  translate(document.body);
  new MutationObserver(records=>{for(const record of records){if(record.type==='characterData')translate(record.target);else if(record.type==='attributes')translate(record.target);else for(const node of record.addedNodes)translate(node);}}).observe(document.body,{childList:true,subtree:true,characterData:true,attributes:true,attributeFilter:['placeholder','title','aria-label','alt']});
  document.title=uzbekAlphabet(document.title);
}
if(typeof module!=='undefined')module.exports=uzbekAlphabet;
