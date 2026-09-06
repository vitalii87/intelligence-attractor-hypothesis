"""Build the self-contained IAH edition. Requires Python/reportlab/Pillow/pypdf and Node/MathJax/sharp/marked.
Environment: IAH_NODE, IAH_NODE_MODULES, IAH_MATHJAX_MODULES. See README.md.
"""
from pathlib import Path
import os,re,json,hashlib,subprocess,html
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image,Table,TableStyle,KeepTogether,Flowable
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader
P=Path(__file__).resolve().parent; ROOT=P.parent; BUILD=P/'.build'; BUILD.mkdir(exist_ok=True)
BASE='https://github.com/vitalii87/intelligence-attractor-hypothesis/blob/main/'
files=[('main','Main text - Canonical statement','ideas/intelligence-attractor-hypothesis.md'),('origin','Origin of the hypothesis and AI assistance','PROVENANCE.md'),('appendix-a','Appendix A - Origin Dependence and Attenuation','ideas/origin-dependence-and-attenuation.md'),('appendix-b','Appendix B - Recursive Architectural Attractor','ideas/recursive-architectural-attractor.md'),('appendix-c','Appendix C - Relational Narrowing and Strong Functional Uniqueness','ideas/relational-narrowing-and-strong-functional-uniqueness.md'),('appendix-d','Appendix D - Related Work Map','ideas/related-work.md'),('appendix-e','Appendix E - Speculative Limits','ideas/speculative-limits.md'),('references','References','paper/references.md')]
pathkeys={f:k for k,t,f in files}
def clean(text,src):
    # Only remove standalone repository-navigation and repeated edition headers.
    text=re.sub(r'^# .+\n','',text,count=1)
    text=re.sub(r'^\[←.*?\n','',text,flags=re.M)
    text=re.sub(r'^\*\*(Author|Initial formulation|Revision):\*\*.*\n','',text,flags=re.M)
    text=re.sub(r'^\*\*Publication preparation:\*\*.*\n','',text,flags=re.M)
    def links(m):
        label,url=m.group(1),m.group(2)
        if '://' in url or url.startswith('#'): return m.group(0)
        resolved=(ROOT/src).parent.joinpath(url).resolve()
        try: rel=resolved.relative_to(ROOT).as_posix()
        except ValueError: raise ValueError('Link outside repository: '+url)
        return '['+label+'](' + ('#'+pathkeys[rel] if rel in pathkeys else BASE+rel) + ')'
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',links,text)
    return text.strip()

chapters=[dict(key='preface',title='Publication scope and interpretive notes',text=clean((P/'front-matter.md').read_text(encoding='utf-8'),'paper/front-matter.md'))]
for k,t,f in files:
    text=clean((ROOT/f).read_text(encoding='utf-8'),f)
    if k.startswith('appendix-'):
        letter=k[-1].upper()
        text=re.sub(r'^## (\d+)\. ',lambda m:'## '+letter+'.'+m[1]+' ',text,flags=re.M)
    chapters.append(dict(key=k,title=t,text=text))
assembled='# The Intelligence Attractor Hypothesis\n\n'
assembled+='\n\n'.join('# '+c['title']+'\n\n'+c['text'] for c in chapters)
(P/'manuscript.md').write_text(assembled+'\n',encoding='utf-8')

math={}
def addmath(tex,display):
    digest=hashlib.sha256((str(display)+tex).encode()).hexdigest()[:20]
    math[digest]={'tex':tex,'display':display}
    return ('\n\nMATHBLOCK'+digest+'\n\n') if display else 'MATHINLINE'+digest
for c in chapters:
    s=re.sub(r'\$\$(.*?)\$\$',lambda m:addmath(m[1].strip(),True),c['text'],flags=re.S)
    s=re.sub(r'\\\((.*?)\\\)',lambda m:addmath(m[1],False),s,flags=re.S)
    c['parsed_source']=s
(BUILD/'input.json').write_text(json.dumps({'chapters':chapters,'math':math}),encoding='utf-8')
subprocess.run([os.environ.get('IAH_NODE','node'),str(P/'render_math.cjs'),str(BUILD)],check=True)
data=json.loads((BUILD/'parsed.json').read_text(encoding='utf-8'))
mathmeta=data['math']

fontdir=Path(os.environ.get('IAH_FONT_DIR','C:/Windows/Fonts'))
for name,file in [('Text','times.ttf'),('Text-Bold','timesbd.ttf'),('Text-Italic','timesi.ttf'),('Text-BoldItalic','timesbi.ttf'),('Sans','arial.ttf'),('Sans-Bold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
pdfmetrics.registerFontFamily('Text',normal='Text',bold='Text-Bold',italic='Text-Italic',boldItalic='Text-BoldItalic')
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Sans-Bold',italic='Sans',boldItalic='Sans-Bold')
WIDTH=A4[0]-100
styles={
 'body':ParagraphStyle('body',fontName='Text',fontSize=11,leading=15,spaceAfter=7),
 'small':ParagraphStyle('small',fontName='Text',fontSize=9.5,leading=12,spaceAfter=5),
 'quote':ParagraphStyle('quote',fontName='Text',fontSize=11,leading=15,leftIndent=16,rightIndent=8,spaceAfter=9,borderPadding=5,textColor=colors.HexColor('#183D4A')),
 'list':ParagraphStyle('list',fontName='Text',fontSize=11,leading=15,leftIndent=15,firstLineIndent=-12,spaceAfter=4),
 'h1':ParagraphStyle('h1',fontName='Sans-Bold',fontSize=20,leading=25,spaceAfter=16,keepWithNext=True,textColor=colors.HexColor('#153B4B')),
 'h2':ParagraphStyle('h2',fontName='Sans-Bold',fontSize=12,leading=16,spaceBefore=12,spaceAfter=7,keepWithNext=True,textColor=colors.HexColor('#153B4B')),
 'h3':ParagraphStyle('h3',fontName='Sans-Bold',fontSize=10.5,leading=14,spaceBefore=8,spaceAfter=5,keepWithNext=True),
 'cover':ParagraphStyle('cover',fontName='Sans-Bold',fontSize=28,leading=33,spaceAfter=18,textColor=colors.HexColor('#153B4B')),
 'subtitle':ParagraphStyle('subtitle',fontName='Text',fontSize=16,leading=22,spaceAfter=18),
}
def textxml(s,size=11):
    # Protect math placeholders then render conservative inline Markdown.
    s=html.escape(s).replace('\n',' ')
    def equation(m):
        d=mathmeta[m[1]]; h=size*d['heightEm']; w=size*d['widthEm']; descent=size*d['depthEm']
        return f'<img src="{html.escape(str(BUILD/d["file"]),quote=True)}" width="{w:.3f}" height="{h:.3f}" valign="{-descent:.3f}"/>'
    s=re.sub(r'MATHINLINE([a-f0-9]{20})',equation,s)
    s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:f'<link href="{m[2]}" color="#14617A">{m[1]}</link>',s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
    s=re.sub(r'`([^`]+)`',r'<font name="Sans" size="9">\1</font>',s)
    # Times lacks some Unicode arrows. Use Arial for these individual glyphs.
    s=re.sub(r'([→←↑↓≤≥≠])',r'<font name="Sans">\1</font>',s)
    return s
def para(s,kind='body'):
    return Paragraph(textxml(s,styles[kind].fontSize),styles[kind])
def render(tokens):
    result=[]
    for t in tokens:
        typ=t['type']
        if typ in ['space','hr']: continue
        if typ=='heading': result.append(para(t['text'],'h2' if t['depth']<=2 else 'h3'))
        elif typ in ['paragraph','text']:
            s=t.get('text','')
            match=re.fullmatch(r'MATHBLOCK([a-f0-9]{20})',s.strip())
            if match:
                d=mathmeta[match[1]]; w=d['widthEm']*12; h=d['heightEm']*12
                factor=min(1,WIDTH/w); im=Image(str(BUILD/d['file']),width=w*factor,height=h*factor)
                im.hAlign='CENTER'; result.extend([Spacer(1,4),im,Spacer(1,10)])
            else: result.append(para(s))
        elif typ=='blockquote':
            for x in t['tokens']:
                if x['type'] in ['paragraph','text']: result.append(para(x['text'],'quote'))
                else: result+=render([x])
        elif typ=='list':
            for n,item in enumerate(t['items'],int(t.get('start') or 1)):
                prefix=f'{n}. ' if t['ordered'] else '• '
                ts=item.get('tokens',[])
                if ts and ts[0]['type']=='text':
                    result.append(para(prefix+ts[0]['text'],'list')); result+=render(ts[1:])
                else: result.append(para(prefix+item['text'],'list'))
            result.append(Spacer(1,3))
        elif typ=='table':
            rows=[[para(x['text'],'small') for x in t['header']]]
            rows += [[para(x['text'],'small') for x in row] for row in t['rows']]
            count=len(rows[0]); widths=[WIDTH/count]*count
            if count==2: widths=[WIDTH*.32,WIDTH*.68]
            tab=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EAF0F3')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#BACBD1'))]))
            result.extend([tab,Spacer(1,9)])
        else: raise RuntimeError('Unsupported Markdown token '+typ+': '+str(t)[:150])
    return result
class Doc(SimpleDocTemplate):
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and getattr(f,'chapter_key',None):
            key=f.chapter_key; self.canv.bookmarkPage(key); self.canv.addOutlineEntry(f.getPlainText(),key,0,False)
            self.notify('TOCEntry',(0,f.getPlainText(),self.page,key))
def footer(c,d):
    if d.page==1:return
    c.setFont('Sans',8);c.setFillColor(colors.HexColor('#60727B'))
    c.drawString(50,27,'Zhyliaiev | Intelligence Attractor Hypothesis | v0.1')
    c.drawRightString(A4[0]-50,27,str(d.page))

story=[Spacer(1,65),para('The Intelligence<br/>Attractor Hypothesis','cover')]
# cover uses intentional HTML breaks, unlike normal source text
story=[Spacer(1,65),Paragraph('The Intelligence<br/>Attractor Hypothesis',styles['cover']),para('Independent Convergence Under Shared Reality Constraints','subtitle'),Spacer(1,8),para('Vitalii Zhyliaiev','subtitle'),para('Conceptual preprint with five supporting appendices'),para('Version 0.1 | Prepared 6 September 2026'),Spacer(1,30),para('A developing hypothesis and research program. No empirical validation or peer review is claimed. The related-work map is preliminary and AI-assisted.'),Spacer(1,14),para('This edition preserves both the canonical functional hypotheses and the separately identified maximal conjecture of absolute architectural uniqueness.'),Spacer(1,14),para('[Project repository](https://github.com/vitalii87/intelligence-attractor-hypothesis)'),PageBreak(),para('Contents','h1')]
toc=TableOfContents();toc.levelStyles=[ParagraphStyle('toc',fontName='Text',fontSize=11,leading=17,spaceBefore=9,leftIndent=0,firstLineIndent=0)]
story.extend([toc,PageBreak()])
for n,c in enumerate(data['chapters']):
    if n:story.append(PageBreak())
    heading=para(c['title'],'h1');heading.chapter_key=c['key'];story.append(heading)
    story+=render(c['tokens'])
dest=P/'IAH-v0.1.pdf'
doc=Doc(str(dest),pagesize=A4,leftMargin=50,rightMargin=50,topMargin=44,bottomMargin=47,title='The Intelligence Attractor Hypothesis: Independent Convergence Under Shared Reality Constraints',author='Vitalii Zhyliaiev',subject='Conceptual preprint, version 0.1, with five appendices')
doc.multiBuild(story,onFirstPage=footer,onLaterPages=footer)
reader=PdfReader(str(dest)); alltext='\n'.join(x.extract_text() for x in reader.pages)
assert len(reader.pages)>10
assert 'MATHINLINE' not in alltext and 'MATHBLOCK' not in alltext
for _,title,_ in files: assert title in alltext,title
manifest_sources=['paper/front-matter.md']+[f for _,_,f in files]
report={'pages':len(reader.pages),'math_expressions':len(math),'math_occurrences':len(re.findall('MATH(?:INLINE|BLOCK)', '\n'.join(c['parsed_source'] for c in chapters))),'pdf_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'source_files':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in manifest_sources},'page_text_lengths':[len(p.extract_text()) for p in reader.pages]}
(P/'build-manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(BUILD/'extracted.txt').write_text(alltext,encoding='utf-8')
print(json.dumps(report,indent=2))
