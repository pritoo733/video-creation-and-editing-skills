"""Render deterministic, story-led motion graphics with local Pillow and FFmpeg."""
from functools import lru_cache
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont


GRAPHIC_KINDS = ('process', 'chart', 'cycle', 'comparison')


def ease(value):
    p = max(0.0, min(1.0, float(value)))
    return p * p * (3.0 - 2.0 * p)


def _font(size, width, bold=False):
    scaled = max(10, round(size * width / 1920))
    candidates = (
        ('C:/Windows/Fonts/seguisb.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf'),
        ('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf'),
        ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, scaled)
        except OSError:
            pass
    return ImageFont.load_default(size=scaled)


def _hex(value, fallback):
    value = value if isinstance(value, str) else fallback
    if len(value) != 7 or not value.startswith('#'):
        value = fallback
    try:
        return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))
    except ValueError:
        return tuple(int(fallback[index:index + 2], 16) for index in (1, 3, 5))


@lru_cache(maxsize=3)
def _background(width, height, background, accent):
    """Cache the expensive static color field; each rendered frame gets a copy."""
    top = _hex(background, '#081420')
    bottom = tuple(round(channel * .58) for channel in top)
    gradient = Image.new('RGB', (1, height))
    pixels = gradient.load()
    for y in range(height):
        p = y / max(1, height - 1)
        pixels[0, y] = tuple(round(a + (b - a) * p) for a, b in zip(top, bottom))
    image = gradient.resize((width, height), Image.Resampling.BILINEAR)
    draw = ImageDraw.Draw(image)
    glow = _hex(accent, '#41ddbf')
    # Fixed fine rules and a restrained top-right halo create depth without
    # introducing random particles or motion unrelated to the narration.
    for i in range(1, 9):
        x = round(i * width / 9)
        draw.line((x, 0, x, height), fill=tuple(round(c * .11) for c in glow), width=1)
    draw.ellipse((width * .67, -height * .6, width * 1.13, height * .23),
                 fill=tuple(round(c * .13) for c in glow))
    return image


def _wrap(text, font, maximum, max_lines=2):
    words = str(text).split()
    lines = []
    line = ''
    for word in words:
        candidate = f'{line} {word}'.strip()
        if line and font.getlength(candidate) > maximum:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines[-1] and font.getlength(lines[-1] + '…') > maximum:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + '…'
    return lines


def _text(draw, xy, text, size, width, color, bold=False, anchor='la', max_width=None, max_lines=2, spacing=6):
    font = _font(size, width, bold)
    lines = _wrap(text, font, max_width, max_lines) if max_width else [str(text)]
    x, y = xy
    line_height = max(font.getbbox('Ag')[3] - font.getbbox('Ag')[1], 12)
    if anchor == 'mm':
        y -= ((len(lines) - 1) * (line_height + spacing)) / 2
    for line in lines:
        draw.text((round(x), round(y)), line, font=font, fill=color, anchor=anchor)
        y += line_height + spacing
    return lines


def _lerp(start, end, amount):
    return round(start + (end - start) * amount)


def _draw_header(draw, spec, t, duration, width, height, accent):
    margin = .075 * width
    reveal = ease(t / max(.24, min(.55, duration * .28)))
    title_y = .12 * height + (1 - reveal) * .025 * height
    title_color = tuple(round(241 * reveal) for _ in range(3))
    _text(draw, (margin, title_y), spec.get('title', ''), 58, width, title_color,
          bold=True, max_width=.82 * width, max_lines=2, spacing=2)
    # Time-based rule draw gives every composition a small but purposeful cue.
    rule_y = round(.265 * height)
    rule_end = margin + .23 * width * ease((t - .12) / max(.3, duration * .32))
    draw.rounded_rectangle((round(margin), rule_y, max(round(margin) + 1, round(rule_end)), rule_y + max(3, round(width / 360))),
                           radius=max(1, round(width / 500)), fill=accent)


def _draw_process(draw, labels, t, duration, width, height, accent):
    count = len(labels); left = .15 * width; right = .85 * width; cy = .51 * height
    max_progress = ease((t - .2) / max(.4, duration * .65))
    # The connecting path grows with the narration's ordered stages.
    draw.rounded_rectangle((round(left), round(cy - height * .006), round(right), round(cy + height * .006)),
                           radius=max(2, round(height * .006)), fill='#29424d')
    draw.rounded_rectangle((round(left), round(cy - height * .006), round(left + (right-left)*max_progress), round(cy + height * .006)),
                           radius=max(2, round(height * .006)), fill=accent)
    for index, label in enumerate(labels):
        x = left + (right-left) * index / (count-1)
        stage = index / (count-1)
        local = ease((max_progress - stage + .12) / .24)
        radius = width * (.027 + .006 * local)
        edge = tuple(round(c * .46) for c in accent)
        draw.ellipse((round(x-radius-5), round(cy-radius-5), round(x+radius+5), round(cy+radius+5)), fill='#102a34', outline=edge, width=max(2, round(width/700)))
        draw.ellipse((round(x-radius), round(cy-radius), round(x+radius), round(cy+radius)), fill=accent if local > .55 else '#203842')
        _text(draw, (x, cy), f'{index+1:02}', 31, width, '#071b22' if local > .55 else '#dce8e9', bold=True, anchor='mm')
        label_y = .65 * height + (1-local) * .025 * height
        label_color=tuple(round(a+(b-a)*local) for a,b in zip((128,151,160),(226,238,239)))
        _text(draw, (x, label_y), label, 31, width, label_color, bold=True,
              anchor='mt', max_width=.21*width, max_lines=2, spacing=3)
        if local > .05:
            draw.ellipse((round(x-4), round(cy-radius-16-local*6), round(x+4), round(cy-radius-8-local*6)), fill=accent)


def _draw_chart(draw, spec, t, duration, width, height, accent):
    labels = spec['labels']; values = spec['values']; maximum=max(values)
    left=.31*width; right=.83*width; top=.34*height; row=.112*height; bar_h=.042*height
    for index,(label,value) in enumerate(zip(labels,values)):
        y=top+index*row
        progress=ease((t-.18-index*.13)/max(.36,duration*.55))
        _text(draw,(.085*width,y+bar_h*.52),label,29,width,'#dce8e9',bold=True,anchor='lm',max_width=.19*width,max_lines=2)
        draw.rounded_rectangle((round(left),round(y),round(right),round(y+bar_h)),radius=max(3,round(bar_h/2)),fill='#18303b')
        value_x=left+(right-left)*(value/maximum)*progress
        if value_x>left:
            draw.rounded_rectangle((round(left),round(y),round(value_x),round(y+bar_h)),radius=max(3,round(bar_h/2)),fill=accent)
        shown=value*progress
        label_value=f'{shown:,.0f}{spec.get("unit","")}' if float(value).is_integer() else f'{shown:.1f}{spec.get("unit","")}'
        _text(draw,(.86*width,y+bar_h*.52),label_value,27,width,'#f1f5f3',bold=True,anchor='lm',max_width=.12*width,max_lines=1)
    source=spec['source']
    source_font=_font(19,width)
    for index,line in enumerate(_wrap(source,source_font,.78*width,2)):
        draw.text((round(.085*width),round(.83*height+index*source_font.size*1.25)),line,font=source_font,fill='#9bb3bb')


def _draw_cycle(draw, spec, t, duration, width, height, accent):
    labels=spec['labels']
    cx=.5*width; cy=.55*height; rx=.275*width; ry=.22*height
    progress=ease((t-.15)/max(.45,duration*.65)); points=[]
    for i in range(121):
        angle=-math.pi/2 + 2*math.pi*i/120
        points.append((cx+rx*math.cos(angle),cy+ry*math.sin(angle)))
    visible=max(2,round((len(points)-1)*progress))
    draw.line(points[:visible],fill=tuple(round(c*.32) for c in accent),width=max(3,round(width/320)),joint='curve')
    marker_index=min(len(points)-1,round(progress*(len(points)-1)))
    mx,my=points[marker_index]; marker_r=max(5,round(width*.008))
    draw.ellipse((round(mx-marker_r*1.8),round(my-marker_r*1.8),round(mx+marker_r*1.8),round(my+marker_r*1.8)),fill='#193944')
    draw.ellipse((round(mx-marker_r),round(my-marker_r),round(mx+marker_r),round(my+marker_r)),fill=accent)
    center_label=spec.get('center_label','')
    if center_label:
        if not isinstance(center_label,str) or len(center_label)>35:
            raise ValueError('Cycle center_label must be text of at most 35 characters')
        _text(draw,(cx,cy),center_label,25,width,'#d9e8e9',bold=True,anchor='mm',max_width=.25*width,max_lines=2,spacing=2)
    for index,label in enumerate(labels):
        angle=-math.pi/2 + 2*math.pi*index/len(labels)
        x=cx+rx*math.cos(angle); y=cy+ry*math.sin(angle)
        local=ease((progress-index/len(labels)+.16)/.22)
        r=.031*width
        draw.ellipse((round(x-r-7),round(y-r-7),round(x+r+7),round(y+r+7)),fill='#102b35',outline=accent if local>.45 else '#35505a',width=max(2,round(width/700)))
        draw.ellipse((round(x-r),round(y-r),round(x+r),round(y+r)),fill=accent if local>.45 else '#1c3540')
        _text(draw,(x,y),str(index+1),28,width,'#061820' if local>.45 else '#deebeb',bold=True,anchor='mm')
        # Labels occupy the space outside the loop, anchored away from the center.
        anchor='mt' if abs(math.sin(angle))>.72 and math.sin(angle)>0 else 'mb' if abs(math.sin(angle))>.72 else ('lm' if math.cos(angle)>0 else 'rm')
        lx=x + (math.cos(angle)*.065*width); ly=y + (math.sin(angle)*.065*height)
        label_color=tuple(round(a+(b-a)*local) for a,b in zip((128,151,160),(231,240,241)))
        _text(draw,(lx,ly),label,26,width,label_color,bold=True,
              anchor=anchor,max_width=.23*width,max_lines=2,spacing=3)


def _draw_comparison(draw, spec, t, duration, width, height, accent):
    details=spec['details']; labels=spec['labels']; progress=ease((t-.15)/max(.45,duration*.62))
    gap=.025*width; card_w=.39*width; card_y=.38*height; card_h=.39*height
    colors=(_hex('#32c3a5','#32c3a5'),_hex('#f0b85c','#f0b85c'))
    for index in range(2):
        local=ease((progress-index*.22)/.58)
        x=.085*width+index*(card_w+gap+.04*width)
        dx=(1-local)*(.035*width)*(1 if index==0 else -1)
        box=(round(x+dx),round(card_y),round(x+card_w+dx),round(card_y+card_h))
        draw.rounded_rectangle(box,radius=round(width*.018),fill='#102631',outline=tuple(round(c*.68) for c in colors[index]),width=max(2,round(width/550)))
        _text(draw,(box[0]+.045*width,box[1]+.055*height),labels[index].upper(),25,width,colors[index],bold=True,
              max_width=card_w*.82,max_lines=1)
        detail_color=tuple(round(a+(b-a)*local) for a,b in zip((137,157,164),(238,244,244)))
        _text(draw,(box[0]+.045*width,box[1]+.17*height),details[index],34,width,
              detail_color,bold=True,max_width=card_w*.82,max_lines=3,spacing=9)
    # One understated bridge, instead of an oversized decorative “VS”.
    cx=.5*width; cy=.575*height; r=.032*width
    draw.ellipse((round(cx-r),round(cy-r),round(cx+r),round(cy+r)),fill='#0b1e28',outline=accent,width=max(2,round(width/650)))
    arrow_length=round(.012*width)
    draw.line((round(cx-arrow_length),round(cy),round(cx+arrow_length*.55),round(cy)),fill=accent,width=max(2,round(width/600)))
    draw.polygon([(round(cx+arrow_length),round(cy)),(round(cx+arrow_length*.25),round(cy-arrow_length*.65)),(round(cx+arrow_length*.25),round(cy+arrow_length*.65))],fill=accent)


def draw_frame(spec, t, duration, width, height, palette=None):
    palette=palette or {}
    bg=palette.get('background','#081420'); accent=palette.get('accent','#41ddbf')
    mode=spec.get('kind'); labels=spec.get('labels')
    if mode not in GRAPHIC_KINDS or not isinstance(labels,list) or not 2<=len(labels)<=4:
        raise ValueError('Original graphic requires process, chart, cycle, or comparison and two to four labels')
    if any(not isinstance(label,str) or not label.strip() or len(label)>55 for label in labels):
        raise ValueError('Graphic labels must be non-empty strings of at most 55 characters')
    if len(spec.get('title',''))>90:
        raise ValueError('Graphic title must be at most 90 characters')
    if mode=='chart':
        values=spec.get('values',[])
        if len(values)!=len(labels) or not all(isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v) and v>=0 for v in values) or not max(values):
            raise ValueError('Chart values must be finite nonnegative numbers matching the labels')
        if not isinstance(spec.get('source'),str) or not spec['source'].strip():
            raise ValueError('A factual chart requires its data source')
    if mode=='comparison':
        details=spec.get('details')
        if len(labels)!=2 or not isinstance(details,list) or len(details)!=2 or any(not isinstance(item,str) or not item.strip() or len(item)>100 for item in details):
            raise ValueError('A comparison requires two labels and two concise detail lines')

    accent_rgb=_hex(accent,'#41ddbf')
    image=_background(width,height,bg,accent).copy(); draw=ImageDraw.Draw(image)
    margin=round(.075*width)
    # Fine corner marks create a consistent motion-design frame without a slide border.
    corner=round(.018*width); mark=max(2,round(width/850)); muted=tuple(round(c*.42) for c in accent_rgb)
    for x,sign in ((margin,1),(width-margin,-1)):
        draw.line((x,round(.315*height),x+sign*corner,round(.315*height)),fill=muted,width=mark)
    _draw_header(draw,spec,t,duration,width,height,accent_rgb)
    if mode=='process': _draw_process(draw,labels,t,duration,width,height,accent_rgb)
    elif mode=='chart': _draw_chart(draw,spec,t,duration,width,height,accent_rgb)
    elif mode=='cycle': _draw_cycle(draw,spec,t,duration,width,height,accent_rgb)
    else: _draw_comparison(draw,spec,t,duration,width,height,accent_rgb)
    # Scene progress belongs to the scene, not to the whole video. It gives a
    # subtle sense of time while leaving most of the composition settled/readable.
    progress=ease(t/max(.1,duration))
    y=height-round(.035*height); x=margin; end=width-margin
    draw.rounded_rectangle((x,y,end,y+max(2,round(height/540))),radius=max(1,round(height/540)),fill='#203641')
    draw.rounded_rectangle((x,y,max(x+1,round(x+(end-x)*progress)),y+max(2,round(height/540))),radius=max(1,round(height/540)),fill=accent_rgb)
    return image


def render(spec,duration,width,height,fps,output,ffmpeg,palette=None):
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True)
    if duration<=0 or fps<=0 or width<=0 or height<=0:
        raise ValueError('Graphic duration, dimensions, and frame rate must be positive')
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
