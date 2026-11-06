"""Consistent offline XLSX, DOCX and Unicode PDF reports (standard library only)."""
import datetime as dt
import io
from pathlib import Path
import zipfile
from xml.sax.saxutils import escape
import alphabet
import management
from report_pdf import PDF

ROOT=Path(__file__).parent
APP='TOŞDÖTAU — elektron navbat tizimi'
HEADERS=['Bölim / operator','Çiqarilgan','Jami xizmat körsatilgan','Kelmagan','Ört. kutiş (min)','Ört. xizmat (min)']
RULES='Kutiş: yaratilgandan oxirgi xizmat çaqiruvigaça. Xizmat: oxirgi bosqişda boşlaşdan yakunlaşgaça. Örtaça vaqtlar minutda; jami xizmat körsatilgan — faqat yakunlangan çiptalar; maʼlumot bölmasa —. Yönaltirilgan çipta bir marta sanaladi.'
BLUE='000000';GREEN='000000';LIGHT='FFFFFF'

def clean(value):
    return ''.join(ch for ch in str(value) if ch in '\t\n\r' or ord(ch)>=32)
def x(value):return escape(clean(value))
def number(value):return '—' if value is None else str(value)

def snapshot(c,start,end,*,sample=False):
    start=dt.date.fromisoformat(start).isoformat();end=dt.date.fromisoformat(end).isoformat()
    report=management.report(c,start,end);settings=management.settings(c)
    names={str(row['id']):row['name'] for row in c.execute('SELECT id,name FROM services')}
    groups=[]
    for key,title in [('services','Bölimlar kesimida'),('employees','Operatorlar kesimida')]:
        rows=[]
        for name,bucket in report[key].items():
            label=names.get(name,name) if key=='services' else 'Biriktirilmagan' if name=='unassigned' else name
            rows.append([label,bucket['issued'],bucket['done'],bucket['absent'],bucket['average_wait_minutes'],bucket['average_service_minutes']])
        groups.append((title,rows))
    summary=[('Çiqarilgan çiptalar',report['issued']),('Jami xizmat körsatilgan',report['served']),('Kelmaganlar',report['absent']),('Hozir kutayotganlar',report['waiting']),('Örtaça kutiş (minut)',report['average_wait_minutes']),('Örtaça xizmat (minut)',report['average_service_minutes'])]
    logo_row=c.execute('SELECT content,mime FROM branding WHERE id=1').fetchone()
    logo=bytes(logo_row['content']) if logo_row and logo_row['mime']=='image/png' else None
    default=ROOT/'web'/'assets'/'university-logo.png'
    if logo is None and default.is_file():logo=default.read_bytes()
    return dict(university=settings['university'],start=start,end=end,generated=dt.datetime.now(dt.timezone(dt.timedelta(hours=5))).strftime('%d.%m.%Y %H:%M'),summary=summary,groups=groups,logo=logo,sample=sample)

def zip_bytes(files):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,data in files.items():archive.writestr(name,data)
    return out.getvalue()


def xlsx(data):
    files={};ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main';relations='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    styles='''<styleSheet xmlns="%s"><numFmts count="1"><numFmt numFmtId="164" formatCode="0.0"/></numFmts><fonts count="3"><font><sz val="11"/><name val="Calibri"/><color rgb="FF000000"/></font><font><sz val="19"/><name val="Calibri"/><b/><color rgb="FF000000"/></font><font><sz val="11"/><name val="Calibri"/><b/><color rgb="FF000000"/></font></fonts><fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFFFFF"/></patternFill></fill><fill><patternFill patternType="solid"><fgColor rgb="FFFFFFFF"/></patternFill></fill></fills><borders count="2"><border/><border><left style="thin"><color rgb="FF000000"/></left><right style="thin"><color rgb="FF000000"/></right><top style="thin"><color rgb="FF000000"/></top><bottom style="thin"><color rgb="FF000000"/></bottom></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="6"><xf fontId="0" fillId="0" borderId="1" xfId="0" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf><xf fontId="1" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf><xf fontId="2" fillId="2" borderId="1" xfId="0" applyFill="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf><xf fontId="0" fillId="3" borderId="1" xfId="0" applyFill="1" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf><xf numFmtId="1" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment vertical="center" horizontal="center"/></xf><xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment vertical="center" horizontal="center"/></xf></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'''%ns
    files['xl/styles.xml']=styles
    sheets=[('Umumiy',None),('Bölimlar',data['groups'][0][1]),('Operatorlar',data['groups'][1][1])]
    sheet_xml=[];book_rels=[];overrides=[];defined=[]
    for index,(name,rows) in enumerate(sheets,1):
        cells={};merges=['A1:E2','A3:E3','A4:E4'];heights={1:26,2:22,3:25,4:25,6:30}
        def cell(r,col,value,style=0):
            ref=chr(65+col)+str(r)
            if isinstance(value,(int,float)) and not isinstance(value,bool):value_xml=f'<v>{value}</v>';typ=''
            else:value_xml='<is><t xml:space="preserve">'+x(number(value))+'</t></is>';typ=' t="inlineStr"'
            cells.setdefault(r,[]).append(f'<c r="{ref}" s="{style}"{typ}>{value_xml}</c>')
        cell(1,0,data['university'],1);cell(3,0,APP);cell(4,0,f"Davr: {data['start']} — {data['end']} | Tayyorlandi: {data['generated']} (UTC+5)")
        cell(6,0,('NAMUNA — SINOV MAʼLUMOTLARI | ' if data['sample'] else '')+name,2);merges.append('A6:F6')
        if rows is None:
            for r,(label,value) in enumerate(data['summary'],7):
                cell(r,0,label,3);cell(r,4,value,5 if r>=11 else 4);merges.extend([f'A{r}:D{r}',f'E{r}:F{r}']);heights[r]=29
            cell(15,0,RULES);merges.append('A15:F17');heights[15]=50;end=17
        else:
            for col,label in enumerate(HEADERS):cell(7,col,label,2)
            heights[7]=37
            for r,row in enumerate(rows,8):
                for col,value in enumerate(row):cell(r,col,value,0 if col==0 else 5 if col>=4 else 4)
                heights[r]=max(28,16*((len(str(row[0]))//55)+1))
            end=max(8,len(rows)+7)
            if not rows:cell(8,0,'Bu davr uçun maʼlumot yo‘q');merges.append('A8:F8')
        drawing=''
        if data['logo']:
            files[f'xl/worksheets/_rels/sheet{index}.xml.rels']=f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="logo" Type="{relations}/drawing" Target="../drawings/drawing{index}.xml"/></Relationships>'
            files[f'xl/drawings/drawing{index}.xml']='''<xdr:wsDr xmlns:xdr="http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="%s"><xdr:oneCellAnchor><xdr:from><xdr:col>5</xdr:col><xdr:colOff>95250</xdr:colOff><xdr:row>0</xdr:row><xdr:rowOff>47625</xdr:rowOff></xdr:from><xdr:ext cx="857250" cy="857250"/><xdr:pic><xdr:nvPicPr><xdr:cNvPr id="1" name="Universitet logotipi"/><xdr:cNvPicPr/></xdr:nvPicPr><xdr:blipFill><a:blip r:embed="image"/><a:stretch><a:fillRect/></a:stretch></xdr:blipFill><xdr:spPr><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></xdr:spPr></xdr:pic><xdr:clientData/></xdr:oneCellAnchor></xdr:wsDr>'''%relations
            files[f'xl/drawings/_rels/drawing{index}.xml.rels']=f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="image" Type="{relations}/image" Target="../media/logo.png"/></Relationships>'
            overrides.append(f'<Override PartName="/xl/drawings/drawing{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/>');drawing='<drawing r:id="logo"/>'
        body=''.join(f'<row r="{r}" ht="{heights.get(r,26)}" customHeight="1">'+''.join(cells[r])+'</row>' for r in sorted(cells))
        files[f'xl/worksheets/sheet{index}.xml']=f'<worksheet xmlns="{ns}" xmlns:r="{relations}"><sheetPr><pageSetUpPr fitToPage="1"/></sheetPr><sheetViews><sheetView workbookViewId="0"><pane ySplit="7" topLeftCell="A8" state="frozen"/></sheetView></sheetViews><cols><col min="1" max="1" width="61" customWidth="1"/><col min="2" max="6" width="18" customWidth="1"/></cols><sheetData>{body}</sheetData>'+('' if rows is None else f'<autoFilter ref="A7:F{end}"/>')+'<mergeCells>'+''.join(f'<mergeCell ref="{m}"/>' for m in merges)+'</mergeCells><pageMargins left="0.3" right="0.3" top="0.4" bottom="0.4" header="0.2" footer="0.2"/><pageSetup paperSize="9" orientation="landscape" fitToWidth="1" fitToHeight="0"/><headerFooter><oddFooter>&amp;LTOŞDÖTAU&amp;R&amp;P / &amp;N</oddFooter></headerFooter>'+drawing+'</worksheet>'
        sheet_xml.append(f'<sheet name="{name}" sheetId="{index}" r:id="s{index}"/>');book_rels.append(f'<Relationship Id="s{index}" Type="{relations}/worksheet" Target="worksheets/sheet{index}.xml"/>');overrides.append(f'<Override PartName="/xl/worksheets/sheet{index}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>');defined.append(f'<definedName name="_xlnm.Print_Area" localSheetId="{index-1}">\'{name}\'!$A$1:$F${end}</definedName>')
    if data['logo']:files['xl/media/logo.png']=data['logo']
    files['xl/workbook.xml']=f'<workbook xmlns="{ns}" xmlns:r="{relations}"><sheets>'+''.join(sheet_xml)+'</sheets><definedNames>'+''.join(defined)+'</definedNames></workbook>'
    files['xl/_rels/workbook.xml.rels']='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(book_rels)+f'<Relationship Id="styles" Type="{relations}/styles" Target="styles.xml"/></Relationships>'
    files['_rels/.rels']=f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="workbook" Type="{relations}/officeDocument" Target="xl/workbook.xml"/></Relationships>'
    files['[Content_Types].xml']='<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'+''.join(overrides)+'</Types>'
    return zip_bytes(files)


def docx(data):
    w='http://schemas.openxmlformats.org/wordprocessingml/2006/main';r='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    def paragraph(text,size=22,bold=False,color=BLUE):return f'<w:p><w:pPr><w:spacing w:after="120"/><w:keepNext/></w:pPr><w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="{size}"/><w:color w:val="{color}"/>'+('<w:b/>' if bold else '')+'</w:rPr><w:t xml:space="preserve">'+x(text)+'</w:t></w:r></w:p>'
    def table(rows,widths,header=True):
        out='<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders><w:top w:val="single" w:sz="4" w:color="000000"/><w:left w:val="single" w:sz="4" w:color="000000"/><w:bottom w:val="single" w:sz="4" w:color="000000"/><w:right w:val="single" w:sz="4" w:color="000000"/><w:insideH w:val="single" w:sz="4" w:color="000000"/><w:insideV w:val="single" w:sz="4" w:color="000000"/></w:tblBorders><w:tblCellMar><w:top w:w="90" w:type="dxa"/><w:bottom w:w="90" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>'+''.join(f'<w:gridCol w:w="{n}"/>' for n in widths)+'</w:tblGrid>'
        for i,row in enumerate(rows):
            out+='<w:tr><w:trPr><w:cantSplit/>'+('<w:tblHeader/>' if header and i==0 else '')+'</w:trPr>'
            for col,value in enumerate(row):
                background='FFFFFF'
                out+=f'<w:tc><w:tcPr><w:tcW w:w="{widths[col]}" w:type="dxa"/><w:shd w:fill="{background}"/></w:tcPr><w:p><w:r><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="19"/><w:color w:val="'+BLUE+'"/>'+('<w:b/>' if header and i==0 else '')+'</w:rPr><w:t xml:space="preserve">'+x(number(value))+'</w:t></w:r></w:p></w:tc>'
            out+='</w:tr>'
        return out+'</w:tbl>'
    logo=''
    if data['logo']:
        logo=f'''<w:p><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"><wp:extent cx="640000" cy="640000"/><wp:docPr id="1" name="Universitet logotipi"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="1" name="logo.png"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="logo"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="640000" cy="640000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''
    branding=logo+paragraph(data['university'],27,True)+paragraph(APP,22)
    if data['sample']:branding+=paragraph('NAMUNA — SINOV MAʼLUMOTLARI',20,True,GREEN)
    content=branding+paragraph('ELEKTRON NAVBAT HISOBOTI',33,True)+paragraph(f"Davr: {data['start']} — {data['end']}  |  Tayyorlandi: {data['generated']} (UTC+5)",19)
    content+=paragraph('Umumiy natijalar',25,True)+table([['Körsatkiç','Natija']]+data['summary'],[8000,4400])
    content+=paragraph('Hisoblaş qoidalari',21,True)+paragraph(RULES,18)
    for title,rows in data['groups']:
        content+='<w:p><w:r><w:br w:type="page"/></w:r></w:p>'+branding+paragraph(f"Davr: {data['start']} — {data['end']}",19)+paragraph(title,25,True)+table([HEADERS]+(rows or [['Maʼlumot yo‘q','—','—','—','—','—']]),[4900,1100,1200,1100,2050,2050])
    import re
    for tag in ('wp:docPr','pic:cNvPr'):
        ids=iter(range(1,1000000))
        content=re.sub(r'(<'+tag+r' id=")1(")',lambda m:m[1]+str(next(ids))+m[2],content)
    sections='<w:sectPr><w:footerReference w:type="default" r:id="footer"/><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/><w:pgMar w:top="700" w:right="700" w:bottom="700" w:left="700" w:header="300" w:footer="300"/></w:sectPr>'
    files={'word/document.xml':f'<w:document xmlns:w="{w}" xmlns:r="{r}"><w:body>{content}{sections}</w:body></w:document>',
      'word/footer.xml':f'<w:ftr xmlns:w="{w}"><w:p><w:pPr><w:jc w:val="right"/></w:pPr><w:r><w:t>TOŞDÖTAU · Sahifa </w:t></w:r><w:fldSimple w:instr="PAGE"/></w:p></w:ftr>',
      '_rels/.rels':f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="doc" Type="{r}/officeDocument" Target="word/document.xml"/></Relationships>',
      'word/_rels/document.xml.rels':f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="footer" Type="{r}/footer" Target="footer.xml"/>'+ (f'<Relationship Id="logo" Type="{r}/image" Target="media/logo.png"/>' if data['logo'] else '')+'</Relationships>',
      '[Content_Types].xml':'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/footer.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/></Types>'}
    if data['logo']:files['word/media/logo.png']=data['logo']
    return zip_bytes(files)


def pdf(data):
    document=PDF((ROOT/'fonts'/'DejaVuSans.ttf').read_bytes());y=0
    def header():
        nonlocal y
        document.new_page()
        if data['logo']:document.image(data['logo'],40,527,52)
        left=107 if data['logo'] else 40
        lines=document.font.wrap(data['university'],842-left-40,12)
        for n,line in enumerate(lines[:2]):document.text(left,566-n*15,line,12,(0,0,0))
        document.text(left,526,APP,11,(0,0,0));document.text(40,492,'ELEKTRON NAVBAT HISOBOTI',18,(0,0,0))
        document.text(40,475,f"Davr: {data['start']} — {data['end']} | Tayyorlandi: {data['generated']} (UTC+5)",9,(0,0,0));y=449
        if data['sample']:document.text(40,y,'NAMUNA — SINOV MAʼLUMOTLARI',10,(0,0,0));y-=23
    def section(title):
        nonlocal y
        if y<100:header()
        document.text(40,y,title,13,(0,0,0));y-=20
    def table(rows,widths,repeat=None):
        nonlocal y
        for row in rows:
            wrapped=[document.font.wrap(number(v),widths[i]-14,9) for i,v in enumerate(row)]
            height=max(len(lines) for lines in wrapped)*12+16
            if y-height<45:
                header()
                if repeat:table([repeat],widths)
            left=40
            for i,lines in enumerate(wrapped):
                document.cell_border(left,y-height,widths[i],height)
                for n,line in enumerate(lines):document.text(left+7,y-17-n*12,line,9,(0,0,0))
                left+=widths[i]
            y-=height
        y-=24
    header();section('Umumiy natijalar')
    table([['Körsatkiç','Natija']]+data['summary'],[520,242],['Körsatkiç','Natija'])
    section('Hisoblaş qoidalari')
    for line in document.font.wrap(RULES,762,9):document.text(40,y,line,9,(0,0,0));y-=13
    for title,rows in data['groups']:
        header();section(title);table([HEADERS]+(rows or [['Maʼlumot yo‘q','—','—','—','—','—']]),[302,65,75,70,125,125],HEADERS)
    return document.bytes()

FORMATS={'xlsx':('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',xlsx),'docx':('application/vnd.openxmlformats-officedocument.wordprocessingml.document',docx),'pdf':('application/pdf',pdf)}

def render(data,fmt):
    if fmt not in FORMATS:raise ValueError('Format: xlsx, docx yoki pdf')
    mime,writer=FORMATS[fmt];return writer(data),mime,f"TOShDOTAU-hisobot-{data['start']}-{data['end']}.{fmt}"
