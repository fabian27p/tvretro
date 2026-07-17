import threading
from datetime import datetime
class StandbyClock:
    def __init__(self,player,settings): self.p=player; self.s=settings; self.stop_evt=threading.Event(); self.th=None
    def start(self):
        self.stop(); self.stop_evt.clear(); self.p.command('loadfile','av://lavfi:color=c=black:s=1280x720:r=1','replace')
        self.th=threading.Thread(target=self.loop,daemon=True); self.th.start()
    def loop(self):
        while not self.stop_evt.is_set():
            fmt='%I:%M %p' if self.s.get('standby','clock_format')=='12h' else '%H:%M'
            t=datetime.now().strftime(fmt)
            if self.s.get('standby','show_date'): t+='\n'+datetime.now().strftime('%d-%m-%Y')
            self.p.show(t,1500); self.stop_evt.wait(1)
    def stop(self): self.stop_evt.set(); self.th.join(timeout=1) if self.th and self.th.is_alive() else None; self.th=None
