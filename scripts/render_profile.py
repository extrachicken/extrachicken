"""Render the visible SVG introduction from the image alt text in README.md."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import re
import textwrap
import xml.etree.ElementTree as ET

NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
class ProfileImage(HTMLParser):
    intro=''
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='img' and attrs.get('src','').startswith('assets/profile-motion.svg'):
            self.intro=attrs.get('alt','').split('Email:')[0].strip()

def render(root):
    readme=root/'README.md'
    source=readme.read_text()
    parser=ProfileImage();parser.feed(source)
    intro=' '.join(parser.intro.split())
    if not intro or len(intro)>1000:
        raise ValueError('Set the profile image alt text in README.md (1–1000 characters).')
    for mobile in (False,True):
        filename='profile-motion-mobile.svg' if mobile else 'profile-motion.svg'
        path=root/'assets'/filename
        svg=ET.fromstring(path.read_text())
        lines=textwrap.wrap(intro,width=30 if mobile else 34)
        line_height=29 if mobile else 35
        extra=max(0,len(lines)-(6 if mobile else 4))*line_height
        width,height=(420,490+extra) if mobile else (960,380+extra)
        svg.set('height',str(height));svg.set('viewBox',f'0 0 {width} {height}')
        svg.find(f'{{{NS}}}title').text=intro
        for node in list(svg):
            if node.tag==f'{{{NS}}}text' and node.find(f'{{{NS}}}tspan') is not None:
                svg.remove(node)
        count=0
        for row,line in enumerate(lines):
            el=ET.SubElement(svg,f'{{{NS}}}text',{'x':'24' if mobile else '550','y':str((116 if mobile else 96)+row*line_height),'style':f'font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;font-size:{23 if mobile else 25}px;fill:#79c7ed'})
            for char in line:
                span=ET.SubElement(el,f'{{{NS}}}tspan',{'class':'letter','style':f'animation-delay:{.25+count*.009:.3f}s','{http://www.w3.org/XML/1998/namespace}space':'preserve'})
                span.text=char;count+=1
        graph_y=(360 if mobile else 254)+extra
        svg.find(f'.//{{{NS}}}clipPath/{{{NS}}}rect').set('y',str(graph_y))
        graph=next(el for el in svg if el.get('clip-path')=='url(#calendar)')
        graph.find(f'{{{NS}}}g').set('transform',f'translate(24 {graph_y})')
        for el in svg.findall(f'{{{NS}}}text'):
            if el.text=='readme.md':
                el.set('y','32')
            elif el.get('class')=='muted':
                el.set('y',str((315 if mobile else 213)+extra if el.text=='C# · Python · TypeScript' else (470 if mobile else 356)+extra))
        path.write_text(ET.tostring(svg,encoding='unicode')+'\n')
    # The new URLs also invalidate GitHub's image cache after a text edit.
    version=hashlib.sha256(''.join((root/'assets'/name).read_text() for name in ['profile-motion.svg','profile-motion-mobile.svg']).encode()).hexdigest()[:12]
    source=re.sub(r'(assets/profile-motion(?:-mobile)?\.svg)(?:\?v=[a-f0-9]+)?',lambda m:m[1]+'?v='+version,source)
    readme.write_text(source)
    return intro

if __name__=='__main__':
    print(render(Path(__file__).resolve().parent.parent))
