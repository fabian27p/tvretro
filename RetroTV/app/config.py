from __future__ import annotations
import json, os
from copy import deepcopy
from pathlib import Path
DEFAULTS={
 "general":{"max_channels":12,"default_channel":1,"remember_last_channel":True,"device_name":"RetroTV"},
 "playback":{"mode":"random","avoid_immediate_repeat":True,"skip_empty_channels":False,"supported_extensions":[".mp4",".mkv",".m4v",".mov"]},
 "display":{"show_osd":True,"osd_duration_seconds":2},
 "audio":{"volume":70,"max_volume":100,"muted":False},
 "effects":{"startup_enabled":True,"shutdown_enabled":True,"channel_change_enabled":True,"static_duration_seconds":0.5},
 "standby":{"enabled":True,"show_clock":True,"clock_format":"24h","show_date":False},
 "ir":{"enabled":False,"gpio_bcm":6,"protocol":"auto"},
 "paths":{"base":"/home/retro/RetroTV","channels":"/home/retro/RetroTV/channels","assets":"/home/retro/RetroTV/assets","logs":"/home/retro/RetroTV/logs","backups":"/home/retro/RetroTV/backups"}
}
def merge(a,b):
    o=deepcopy(a)
    for k,v in b.items(): o[k]=merge(o[k],v) if isinstance(v,dict) and isinstance(o.get(k),dict) else v
    return o
def atomic_write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)
class Settings:
    def __init__(self,path): self.path=Path(path); self.data=deepcopy(DEFAULTS)
    def load(self):
        if not self.path.exists(): atomic_write(self.path,self.data); return
        try: self.data=merge(DEFAULTS,json.loads(self.path.read_text(encoding='utf-8')))
        except Exception: atomic_write(self.path,self.data)
    def save(self): atomic_write(self.path,self.data)
    def get(self,*keys,default=None):
        cur=self.data
        for k in keys:
            if not isinstance(cur,dict) or k not in cur: return default
            cur=cur[k]
        return cur
    def set(self,value,*keys):
        cur=self.data
        for k in keys[:-1]: cur=cur.setdefault(k,{})
        cur[keys[-1]]=value
