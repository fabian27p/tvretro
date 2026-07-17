import random
from pathlib import Path
class ChannelLibrary:
    def __init__(self,path,max_channels,extensions): self.path=Path(path); self.max_channels=max_channels; self.ext={e.lower() for e in extensions}
    def root(self,n): return self.path/f"channel{n:02d}"
    def videos(self,n):
        r=self.root(n)
        if not r.exists(): return []
        return sorted([p for p in r.rglob('*') if p.is_file() and not p.name.startswith('.') and p.suffix.lower() in self.ext],key=lambda p:str(p).lower())
    def name(self,n):
        r=self.root(n); ds=[p for p in r.iterdir() if p.is_dir() and not p.name.startswith('.')] if r.exists() else []
        return ds[0].name if len(ds)==1 else ('SIN SEÑAL' if not ds else f'{len(ds)} carpetas')
    def choose(self,n,mode,previous=None):
        vs=self.videos(n)
        if not vs: return None
        if mode=='sequential':
            if previous in [str(v) for v in vs]: return vs[([str(v) for v in vs].index(previous)+1)%len(vs)]
            return vs[0]
        c=[v for v in vs if str(v)!=previous] or vs
        return random.choice(c)
    def wrap(self,n): return self.max_channels if n<1 else 1 if n>self.max_channels else n
