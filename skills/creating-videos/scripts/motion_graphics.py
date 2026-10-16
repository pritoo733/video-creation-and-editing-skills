"""Original process reveals and data-driven charts; no hosted generation service."""
import math
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw, ImageFont


def ease(value):
    p=max(0,min(1,value)); return p*p*(3-2*p)


def draw_frame(spec, t, duration, width, height, palette=None):
    palette=palette or {}; bg=palette.get('background','#081420'); accent=palette.get('accent','#41ddbf')
    mode=spec['kind']; labels=spec['labels']
    if mode not in ('process','chart') or not 2 <= len(labels) <= 4:
        raise ValueError('Original graphic requires process/chart and two to four labels')
    if any(len(label)>30 for label in labels) or len(spec.get('title',''))>65:
        raise ValueError('Graphic text is too long; shorten it before rendering')
    if mode=='chart':
        values=spec.get('values',[])
        if len(values)!=len(labels) or not all(isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v) and v>=0 for v in values) or not max(values):
            raise ValueError('Chart values must be finite nonnegative numbers matching the labels')
        if not spec.get('source'):
            raise ValueError('A factual chart requires its data source')
    im=Image.new('RGB',(width,height),bg); draw=ImageDraw.Draw(im)
    font=lambda size: ImageFont.load_default(size=max(10,round(size*width/1920)))
    def text(x,y,label,size,color='#f1f5f3'):
        draw.text((round(x*width),round(y*height)),str(label),font=font(size),fill=color)
    # Quiet architectural lines provide depth without moving the entire canvas.
    for i in range(1,8):
        x=round(i*width/8); draw.line((x,0,x,height),fill='#112634',width=1)
    text(.07,.12,spec.get('title',''),60)
    progress=ease((t-.35)/max(.1,duration-1.0))
    if mode=='process':
        y=round(.49*height); left=.12*width; right=.88*width
        draw.line((left,y,right,y),fill='#25404d',width=max(2,round(width/380)))
        draw.line((left,y,left+(right-left)*progress,y),fill=accent,width=max(2,round(width/380)))
        for i,label in enumerate(labels):
            x=round(left+(right-left)*i/(len(labels)-1)); active=progress >= i/(len(labels)-1)
            radius=round(width*.026)
            draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill=accent if active else '#203644')
            text(x/width-.008,.49-.018,str(i+1),36,'#06151d' if active else '#e0e9e9')
            line1,line2=label,''
            if len(label)>17:
                words=label.split(); pivot=max(1,len(words)//2); line1=' '.join(words[:pivot]); line2=' '.join(words[pivot:])
            text(x/width-.08,.61,line1,32)
            if line2: text(x/width-.08,.67,line2,32)
    else:
        maximum=max(spec['values'])
        for i,(label,value) in enumerate(zip(labels,spec['values'])):
            y=.32+i*.12; reveal=ease((t-.3-i*.15)/max(.3,duration-1.5))
            text(.07,y,label,30)
            x1=round(.30*width); x2=round((.30+.48*value/maximum*reveal)*width)
            draw.rounded_rectangle((x1,round(y*height),max(x1+1,x2),round((y+.055)*height)),radius=max(1,width//200),fill=accent)
            if reveal>.95: text(.81,y,f'{value:g}{spec.get("unit","")}',32)
        text(.07,.82,spec['source'][:110],22,'#a8bdc2')
    return im


def render(spec,duration,width,height,fps,output,ffmpeg,palette=None):
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True)
    # Validate before launching the encoder, so bad data cannot leave a live process.
    draw_frame(spec,0,duration,width,height,palette)
    log=output.with_suffix('.graphic.log')
    command=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
             '-s',f'{width}x{height}','-r',str(fps),'-i','pipe:0','-an','-c:v','libx264',
             '-preset','fast','-crf','18','-pix_fmt','yuv420p',str(output)]
    with log.open('wb') as errors:
        process=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=errors)
        try:
            for frame in range(round(duration*fps)):
                process.stdin.write(draw_frame(spec,frame/fps,duration,width,height,palette).tobytes())
            process.stdin.close(); code=process.wait()
        except BaseException:
            process.stdin.close(); process.wait(); raise
    if code: raise RuntimeError('Graphic render failed: '+log.read_text(errors='replace')[-1000:])
    return str(output)
