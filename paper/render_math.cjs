const fs=require('fs'), path=require('path');
const {createRequire}=require('module');
const normal=createRequire(path.join(process.env.IAH_NODE_MODULES,'_resolver.cjs'));
const mj=createRequire(path.join(process.env.IAH_MATHJAX_MODULES,'_resolver.cjs'));
const sharp=normal('sharp');
const {mathjax}=mj('mathjax-full/js/mathjax.js');
const {TeX}=mj('mathjax-full/js/input/tex.js');
const {SVG}=mj('mathjax-full/js/output/svg.js');
const {liteAdaptor}=mj('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler}=mj('mathjax-full/js/handlers/html.js');
const {AllPackages}=mj('mathjax-full/js/input/tex/AllPackages.js');
const adaptor=liteAdaptor();RegisterHTMLHandler(adaptor);
const doc=mathjax.document('',{InputJax:new TeX({packages:AllPackages}),OutputJax:new SVG({fontCache:'none'})});
async function main(){
 const dir=process.argv[2],data=JSON.parse(fs.readFileSync(path.join(dir,'input.json'),'utf8'));
 const {marked}=await import(require('url').pathToFileURL(normal.resolve('marked')).href);
 const meta={};
 for(const [id,m] of Object.entries(data.math)){
  let tex=m.tex;
  // Wrap long conceptual arrow chains, without changing their order or meaning.
  if(m.display && tex.length>125 && (tex.match(/\\rightarrow/g)||[]).length>=3){
   const a=tex.split('\\rightarrow'), mid=Math.ceil(a.length/2);
   tex='\\begin{gathered}'+a.slice(0,mid).join('\\rightarrow')+'\\\\ \\rightarrow '+a.slice(mid).join('\\rightarrow')+'\\end{gathered}';
  }
  let rendered=adaptor.outerHTML(doc.convert(tex,{display:m.display}));
  if(rendered.includes('data-mjx-error')||rendered.includes('data-mml-node="merror"'))throw Error('Math error '+m.tex+' '+rendered);
  let svg=rendered.slice(rendered.indexOf('<svg'),rendered.lastIndexOf('</svg>')+6);
  const vb=svg.match(/viewBox="([^"]+)"/)[1].split(/\s+/).map(Number), w=vb[2]/1000,h=vb[3]/1000,depth=Math.max(0,(vb[1]+vb[3])/1000);
  svg=svg.replace(/width="[^"]+"/,`width="${w*48}px"`).replace(/height="[^"]+"/,`height="${h*48}px"`).replace(/currentColor/g,'#111111');
  if(!svg.includes('xmlns='))svg=svg.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ');
  const file=id+'.png';await sharp(Buffer.from(svg)).png().toFile(path.join(dir,file));
  meta[id]={file,widthEm:w,heightEm:h,depthEm:depth,display:m.display};
 }
 const chapters=data.chapters.map(c=>({key:c.key,title:c.title,tokens:marked.lexer(c.parsed_source,{gfm:true})}));
 fs.writeFileSync(path.join(dir,'parsed.json'),JSON.stringify({chapters,math:meta}));
 console.log('Typeset '+Object.keys(meta).length+' distinct equations.');
}
main().catch(e=>{console.error(e);process.exit(1)});
