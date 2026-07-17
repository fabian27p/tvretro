import json
from pathlib import Path
from config import atomic_write
DEFAULT={"current_channel":1,"volume":70,"muted":False,"standby":False,"last_video_by_channel":{}}
class StateStore:
    def __init__(self,path): self.path=Path(path); self.data=dict(DEFAULT)
    def load(self):
        try: self.data={**DEFAULT,**json.loads(self.path.read_text(encoding='utf-8'))}
        except Exception: self.save()
    def save(self): atomic_write(self.path,self.data)
    def get(self,k,d=None): return self.data.get(k,d)
    def set(self,k,v,save=False): self.data[k]=v; self.save() if save else None
