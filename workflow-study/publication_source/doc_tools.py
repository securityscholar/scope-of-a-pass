"""Anonymous manuscript formatting; no author or workstation metadata."""
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

def font(style,size,bold=False):
    style.font.name='Times New Roman';style.font.size=Pt(size);style.font.bold=bold;style.font.italic=False;style.font.color.rgb=RGBColor(0,0,0)
    pr=style.element.get_or_add_rPr();rf=pr.find(qn('w:rFonts'))
    if rf is not None:
        for key in list(rf.attrib):
            if 'theme' in key.lower():del rf.attrib[key]
        for key in ('ascii','hAnsi','eastAsia','cs'):rf.set(qn('w:'+key),'Times New Roman')
    for e in pr.findall(qn('w:spacing')):pr.remove(e)
    for pp in style.element.findall(qn('w:pPr')):
        for tag in ('pBdr','numPr'):
            for e in pp.findall(qn('w:'+tag)):pp.remove(e)

def document(header,title,body=12):
    d=Document();s=d.sections[0];s.page_width=Inches(8.5);s.page_height=Inches(11);s.top_margin=Inches(.8);s.bottom_margin=Inches(.8);s.left_margin=Inches(.95);s.right_margin=Inches(.95);s.header_distance=Inches(.32);s.footer_distance=Inches(.32)
    for name in ('Normal','Body Text','Title','Subtitle','Heading 1','Heading 2','Caption'):
        font(d.styles[name],body);p=d.styles[name].paragraph_format;p.space_before=Pt(0);p.space_after=Pt(5);p.line_spacing=1.05
    font(d.styles['Title'],19,True);font(d.styles['Subtitle'],12);d.styles['Subtitle'].paragraph_format.space_after=Pt(11)
    for name in ('Heading 1','Heading 2'):
        font(d.styles[name],body,True);p=d.styles[name].paragraph_format;p.space_before=Pt(9);p.space_after=Pt(5);p.keep_with_next=True
    font(d.styles['Caption'],10,True);d.styles['Caption'].paragraph_format.keep_with_next=True
    h=s.header.paragraphs[0];h.add_run(header).font.size=Pt(9)
    f=s.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER;field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');f._p.append(field)
    for key in ('author','last_modified_by','comments','subject','keywords','category'):setattr(d.core_properties,key,'')
    d.core_properties.title=title;d.core_properties.language='en-US';return d

def link(p,label,url):
    rid=p.part.relate_to(url,RT.HYPERLINK,is_external=True);h=OxmlElement('w:hyperlink');h.set(qn('r:id'),rid);r=OxmlElement('w:r');pr=OxmlElement('w:rPr');sz=OxmlElement('w:sz');sz.set(qn('w:val'),'21');pr.append(sz);r.append(pr);t=OxmlElement('w:t');t.set(qn('xml:space'),'preserve');t.text=label;r.append(t);h.append(r);p._p.append(h)

def references(d,items):
    p=d.add_heading('References',level=1);p.paragraph_format.page_break_before=True
    for text,url in items:
        p=d.add_paragraph();p.paragraph_format.line_spacing=1.0;p.paragraph_format.space_after=Pt(7);p.paragraph_format.keep_together=True;p.paragraph_format.left_indent=Inches(.18);p.paragraph_format.first_line_indent=Inches(-.18);p.add_run(text+' ').font.size=Pt(10.5);link(p,'Source',url)

def table(d,caption,headers,rows,note,widths):
    d.add_paragraph(caption,style='Caption');t=d.add_table(rows=1,cols=len(headers));t.autofit=False
    for cell,text in zip(t.rows[0].cells,headers):cell.text=str(text)
    for row in rows:
        for cell,text in zip(t.add_row().cells,row):cell.text=str(text)
    for i,row in enumerate(t.rows):
        pr=row._tr.get_or_add_trPr();pr.append(OxmlElement('w:cantSplit'))
        if i==0:pr.append(OxmlElement('w:tblHeader'))
        for j,cell in enumerate(row.cells):
            cell.width=Inches(widths[j]);cp=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
            for side in ('top','bottom'):
                e=OxmlElement('w:'+side);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'7' if i==0 else '3');e.set(qn('w:color'),'000000' if i==0 else 'B8B8B8');borders.append(e)
            cp.append(borders)
            for p in cell.paragraphs:
                p.paragraph_format.space_after=Pt(2);p.paragraph_format.line_spacing=1.0;p.paragraph_format.keep_with_next=True
                for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(9.5);r.font.bold=i==0;r.font.italic=False
    p=d.add_paragraph('Note. '+note);p.paragraph_format.keep_together=True
    for r in p.runs:r.font.size=Pt(9.5)

def figure(d,caption,path,note):
    d.add_paragraph(caption,style='Caption');p=d.add_paragraph();p.paragraph_format.keep_with_next=True;p.add_run().add_picture(str(path),width=Inches(6.55));p=d.add_paragraph('Note. '+note);p.paragraph_format.keep_together=True
    for r in p.runs:r.font.size=Pt(9.5)
