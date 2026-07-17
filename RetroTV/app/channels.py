import json,random
from pathlib import Path
class ChannelLibrary:
    def __init__(self,path,max_channels,extensions): self.path=Path(path); self.max_channels=max_channels; self.ext={e.lower() for e in extensions}
    def root(self,n): return self.path/f"channel{n:02d}"
    def metadata(self,n):
        r=self.root(n)
        for name in ('channel.local.json','channel.json','.channel.json'):
            p=r/name
            if p.exists():
                try: return json.loads(p.read_text(encoding='utf-8'))
                except Exception: return {}
        return {}
    def media_root(self,n):
        meta=self.metadata(n)
        if meta.get('path'): return Path(str(meta['path'])).expanduser()
        return self.root(n)
    def videos(self,n):
        r=self.media_root(n)
        if not r.exists(): return []
        ignored={'channel.local.json','channel.json','.channel.json','channel.json.example'}
        return sorted([p for p in r.rglob('*') if p.is_file() and not p.name.startswith('.') and p.name not in ignored and p.suffix.lower() in self.ext],key=lambda p:str(p).lower())
    def name(self,n):
        meta=self.metadata(n)
        if meta.get('name'): return str(meta['name'])
        r=self.media_root(n); ds=[p for p in r.iterdir() if p.is_dir() and not p.name.startswith('.')] if r.exists() else []
        if self.videos(n): return ds[0].name if len(ds)==1 else f'CANAL {n:02d}'
        return 'SIN SEÑAL'
    def choose(self,n,mode,previous=None,avoid_repeat=True):
        vs=self.videos(n)
        if not vs: return None
        if mode=='sequential':
            if previous in [str(v) for v in vs]: return vs[([str(v) for v in vs].index(previous)+1)%len(vs)]
            return vs[0]
        c=[v for v in vs if avoid_repeat and str(v)!=previous] or vs
        return random.choice(c)
    def wrap(self,n): return self.max_channels if n<1 else 1 if n>self.max_channels else n
