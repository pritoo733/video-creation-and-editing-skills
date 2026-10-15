#!/usr/bin/env python3
"""Install both skills and shared templates into a user-selected agent directory."""
import argparse, shutil
from pathlib import Path

def install(source,destination,update=False):
    destination=destination.resolve()
    targets=[destination/name for name in ('creating-videos','editing-videos')]
    if not update and any(p.exists() for p in targets):
        raise ValueError('A skill already exists. Inspect local customizations, then use --update to merge repository files.')
    for target in targets:
        shutil.copytree(source/'skills'/target.name,target,dirs_exist_ok=update,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    templates=targets[0]/'assets/templates'
    shutil.copytree(source/'templates',templates,dirs_exist_ok=True)
    for p in (targets[0]/'references').glob('*.md'):
        original=p.read_text(encoding='utf-8')
        revised=original.replace('../../../templates/','../assets/templates/')
        if revised!=original:p.write_text(revised,encoding='utf-8')
    return targets

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dest',required=True,type=Path,help='The skills directory scanned by your agent')
    p.add_argument('--update',action='store_true',help='Merge repository files into existing skill folders; overwrites matching files')
    args=p.parse_args()
    for target in install(Path(__file__).resolve().parents[1],args.dest,args.update):print(target)
    print('Both skills, scripts, references, and shared templates installed. Discovery depends on the host agent.')

if __name__=='__main__':main()
