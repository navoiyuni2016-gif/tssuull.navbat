"""Small offline Unicode PDF writer using an embedded, licensed TrueType font.
No runtime dependencies; PDF 1.4, Type0/CIDFontType2 with a ToUnicode map.
"""
import functools
import struct
import zlib

class Font:
    def __init__(self,data):
        self.data=data;self.used={};self.tables={}
        for i in range(struct.unpack_from('>H',data,4)[0]):
            tag,_,offset,length=struct.unpack_from('>4sIII',data,12+i*16);self.tables[tag.decode()]=(offset,length)
        self.units=self.u16('head',18);self.metrics=self.u16('hhea',34)
        self.bbox=[round(n*1000/self.units) for n in struct.unpack_from('>hhhh',data,self.tables['head'][0]+36)]
        self.ascent=round(self.i16('hhea',4)*1000/self.units);self.descent=round(self.i16('hhea',6)*1000/self.units)
        cmap=self.tables['cmap'][0];subtables=[]
        for i in range(struct.unpack_from('>H',data,cmap+2)[0]):
            platform,encoding,relative=struct.unpack_from('>HHI',data,cmap+4+i*8);offset=cmap+relative;fmt=struct.unpack_from('>H',data,offset)[0]
            if fmt in (4,12):subtables.append((fmt==12,platform==3,offset,fmt))
        _,_,offset,fmt=max(subtables);self.cmap={}
        if fmt==12:
            for i in range(struct.unpack_from('>I',data,offset+12)[0]):
                start,end,glyph=struct.unpack_from('>III',data,offset+16+i*12)
                for code in range(start,end+1):self.cmap[code]=glyph+code-start
        else:
            count=struct.unpack_from('>H',data,offset+6)[0]//2;end=offset+14;start=end+2*count+2;delta=start+2*count;ro=delta+2*count
            for i in range(count):
                lo,hi=struct.unpack_from('>H',data,start+2*i)[0],struct.unpack_from('>H',data,end+2*i)[0];d=struct.unpack_from('>h',data,delta+2*i)[0];r=struct.unpack_from('>H',data,ro+2*i)[0]
                for code in range(lo,min(hi,65534)+1):
                    glyph=struct.unpack_from('>H',data,ro+2*i+r+2*(code-lo))[0] if r else code
                    self.cmap[code]=(glyph+d)&65535 if glyph else 0
    def u16(self,table,offset):return struct.unpack_from('>H',self.data,self.tables[table][0]+offset)[0]
    def i16(self,table,offset):return struct.unpack_from('>h',self.data,self.tables[table][0]+offset)[0]
    def glyph(self,char):return self.cmap.get(ord(char),self.cmap.get(ord('?'),0))
    def width(self,text,size):return sum(self.advance(self.glyph(c)) for c in str(text))*size/1000
    def advance(self,glyph):return self.u16('hmtx',min(glyph,self.metrics-1)*4)*1000/self.units
    def encode(self,text):
        ids=[]
        for char in str(text):
            gid=self.glyph(char);self.used[gid]=char;ids.append(f'{gid:04X}')
        return ''.join(ids)
    def wrap(self,text,width,size):
        lines=[];line=''
        for word in str(text).split():
            candidate=(line+' '+word).strip()
            if self.width(candidate,size)>width and line:lines.append(line);line=''
            while self.width(word,size)>width:
                n=max(1,int(len(word)*width/max(self.width(word,size),1)))
                lines.append(word[:n]);word=word[n:]
            line=(line+' '+word).strip()
        return lines+[line] if line else lines or ['']

@functools.lru_cache(maxsize=4)
def png_rgb_alpha(data):
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('PNG required')
    offset=8;chunks=[];width=height=color=0
    while offset+12<=len(data):
        length=struct.unpack_from('>I',data,offset)[0];tag=data[offset+4:offset+8];payload=data[offset+8:offset+8+length];offset+=length+12
        if tag==b'IHDR':
            width,height,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',payload)
            if not 1<=width<=2048 or not 1<=height<=2048 or depth!=8 or color not in (2,6) or interlace:raise ValueError('Unsupported PNG')
        elif tag==b'IDAT':chunks.append(payload)
        elif tag==b'IEND':break
    channels=4 if color==6 else 3;stride=width*channels;expected=(stride+1)*height
    raw=zlib.decompressobj().decompress(b''.join(chunks),expected+1)
    if len(raw)!=expected:raise ValueError('Invalid PNG data')
    previous=bytearray(stride);rgb=bytearray();alpha=bytearray();offset=0
    def paeth(a,b,c):
        p=a+b-c;pa=abs(p-a);pb=abs(p-b);pc=abs(p-c)
        return a if pa<=pb and pa<=pc else b if pb<=pc else c
    for _ in range(height):
        kind=raw[offset];row=bytearray(raw[offset+1:offset+1+stride]);offset+=stride+1
        if kind>4:raise ValueError('Invalid PNG filter')
        if kind:
            for i in range(stride):
                a=row[i-channels] if i>=channels else 0;b=previous[i];c=previous[i-channels] if i>=channels else 0
                row[i]=(row[i]+(a if kind==1 else b if kind==2 else (a+b)//2 if kind==3 else paeth(a,b,c)))&255
        if channels==3:rgb.extend(row)
        else:
            for i in range(0,stride,4):rgb.extend(row[i:i+3]);alpha.append(row[i+3])
        previous=row
    return width,height,zlib.compress(rgb),zlib.compress(alpha) if alpha else None


class PDF:
    def __init__(self,font):self.font=Font(font);self.pages=[];self.commands=[];self.objects=[];self.logo=None
    def add(self,data):self.objects.append(data);return len(self.objects)
    def text(self,x,y,text,size=10,color=(.06,.16,.29)):
        self.commands.append(f'{color[0]} {color[1]} {color[2]} rg BT /F1 {size} Tf 1 0 0 1 {x:.2f} {y:.2f} Tm <{self.font.encode(text)}> Tj ET')
    def box(self,x,y,w,h,fill):self.commands.append(f'{fill[0]} {fill[1]} {fill[2]} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f')
    def cell_border(self,x,y,w,h):self.commands.append(f'0 0 0 RG .5 w {x:.2f} {y:.2f} {w:.2f} {h:.2f} re S')
    def line(self,x,y,w,color=(.8,.86,.91)):self.commands.append(f'{color[0]} {color[1]} {color[2]} RG .5 w {x} {y} m {x+w} {y} l S')
    def image(self,data,x,y,size):
        try:self.logo=png_rgb_alpha(data)
        except (ValueError,struct.error,zlib.error):return
        self.commands.append(f'q {size} 0 0 {size} {x} {y} cm /Logo Do Q')
    def new_page(self):
        if self.commands:self.pages.append(self.commands)
        self.commands=[]
    def bytes(self):
        self.new_page();logo_resource=''
        if self.logo:
            width,height,rgb,alpha=self.logo;mask=''
            if alpha:
                ref=self.add(f'<< /Type /XObject /Subtype /Image /Width {width} /Height {height} /ColorSpace /DeviceGray /BitsPerComponent 8 /Length {len(alpha)} /Filter /FlateDecode >>\nstream\n'.encode()+alpha+b'\nendstream');mask=f' /SMask {ref} 0 R'
            ref=self.add(f'<< /Type /XObject /Subtype /Image /Width {width} /Height {height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Length {len(rgb)} /Filter /FlateDecode {mask} >>\nstream\n'.encode()+rgb+b'\nendstream');logo_resource=f' /XObject << /Logo {ref} 0 R >>'
        font_id=self.add(b'');pages_id=self.add(b'');root_id=self.add(b'');page_ids=[]
        for number,commands in enumerate(self.pages,1):
            self.commands=commands
            self.text(40,22,'TOŞDÖTAU  |  '+str(number)+' / '+str(len(self.pages)),8,(.43,.5,.59))
            stream='\n'.join(commands).encode('ascii');packed=zlib.compress(stream)
            stream_id=self.add(b'<< /Length '+str(len(packed)).encode()+b' /Filter /FlateDecode >>\nstream\n'+packed+b'\nendstream')
            page_ids.append(self.add(f'<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 842 595] /Resources << /Font << /F1 {font_id} 0 R >> {logo_resource} >> /Contents {stream_id} 0 R >>'.encode()))
        packed=zlib.compress(self.font.data);file_id=self.add(b'<< /Length '+str(len(packed)).encode()+b' /Length1 '+str(len(self.font.data)).encode()+b' /Filter /FlateDecode >>\nstream\n'+packed+b'\nendstream')
        descriptor=self.add(f'<< /Type /FontDescriptor /FontName /DejaVuSans /Flags 32 /FontBBox [{" ".join(map(str,self.font.bbox))}] /ItalicAngle 0 /Ascent {self.font.ascent} /Descent {self.font.descent} /CapHeight {self.font.ascent} /StemV 80 /FontFile2 {file_id} 0 R >>'.encode())
        widths=' '.join(f'{gid} [{round(self.font.advance(gid))}]' for gid in sorted(self.font.used))
        cid=self.add(f'<< /Type /Font /Subtype /CIDFontType2 /BaseFont /DejaVuSans /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> /FontDescriptor {descriptor} 0 R /CIDToGIDMap /Identity /DW 600 /W [{widths}] >>'.encode())
        cmap='/CIDInit /ProcSet findresource begin 12 dict begin begincmap /CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def /CMapName /Unicode def /CMapType 2 def 1 begincodespacerange <0000> <FFFF> endcodespacerange\n'
        items=list(self.font.used.items())
        for offset in range(0,len(items),100):
            batch=items[offset:offset+100];cmap+=str(len(batch))+' beginbfchar\n'+'\n'.join(f'<{gid:04X}> <{char.encode("utf-16-be").hex()}>' for gid,char in batch)+'\nendbfchar\n'
        cmap+='endcmap CMapName currentdict /CMap defineresource pop end end';raw=cmap.encode();unicode_id=self.add(b'<< /Length '+str(len(raw)).encode()+b' >>\nstream\n'+raw+b'\nendstream')
        self.objects[font_id-1]=f'<< /Type /Font /Subtype /Type0 /BaseFont /DejaVuSans /Encoding /Identity-H /DescendantFonts [{cid} 0 R] /ToUnicode {unicode_id} 0 R >>'.encode()
        self.objects[pages_id-1]=f'<< /Type /Pages /Count {len(page_ids)} /Kids [{" ".join(str(n)+" 0 R" for n in page_ids)}] >>'.encode();self.objects[root_id-1]=f'<< /Type /Catalog /Pages {pages_id} 0 R >>'.encode()
        output=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n');offsets=[0]
        for n,obj in enumerate(self.objects,1):offsets.append(len(output));output+=f'{n} 0 obj\n'.encode()+obj+b'\nendobj\n'
        xref=len(output);output+=f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode()
        for offset in offsets[1:]:output+=f'{offset:010d} 00000 n \n'.encode()
        output+=f'trailer << /Size {len(offsets)} /Root {root_id} 0 R >>\nstartxref\n{xref}\n%%EOF'.encode();return bytes(output)
