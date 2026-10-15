#!/usr/bin/env python3
"""Sample central-content movement. Diagnostic evidence, not a creative quality score."""
import argparse, json, shutil, subprocess
from pathlib import Path

def inspect(video,ffmpeg,rate=2):
    # Sample before resizing to preserve cadence on builds with scale EOF issues.
    vf=f'fps={rate},crop=iw*0.8:ih*0.6:iw*0.1:ih*0.2,scale=64:64,format=gray'
    r=subprocess.run([ffmpeg,'-v','error','-i',str(video),'-vf',vf,'-pix_fmt','gray','-f','rawvideo','pipe:1'],capture_output=True,check=True)
    raw=r.stdout;size=4096;frames=[raw[i:i+size] for i in range(0,len(raw)-size+1,size)]
    samples=[]
    for i,(a,b) in enumerate(zip(frames,frames[1:]),1):
        differences=[abs(x-y) for x,y in zip(a,b)]
        mean=sum(differences)/size;changed=sum(d>5 for d in differences)/size
        samples.append(dict(time=round(i/rate,3),mean_abs_luma_change=round(mean,4),changed_fraction=round(changed,4),near_static=mean<.5 and changed<.015))
    if not samples:raise ValueError('Not enough decoded frames to compare')
    return dict(file=str(video),sample_rate=rate,roi=dict(x=.1,y=.2,width=.8,height=.6),sample_pairs=len(samples),near_static_fraction=sum(s['near_static'] for s in samples)/len(samples),mean_abs_luma_change=sum(s['mean_abs_luma_change'] for s in samples)/len(samples),interpretation='Locate passages for review. Movement may be caused by footage, graphics, cuts, noise, or camera moves; it is not a quality score.',samples=samples)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('video',type=Path)
    p.add_argument('--ffmpeg',default=shutil.which('ffmpeg'));p.add_argument('--output',type=Path)
    args=p.parse_args()
    if not args.ffmpeg:p.error('Supply an installed FFmpeg with --ffmpeg')
    result=inspect(args.video.resolve(),args.ffmpeg)
    if args.output:args.output.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2))

if __name__=='__main__':main()
