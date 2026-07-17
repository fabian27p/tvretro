from __future__ import annotations
import fcntl,os,signal,sys,threading,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from config import Settings
from state import StateStore
from channels import ChannelLibrary
from player import MPVPlayer
from constants import LOCK_FILE,MPV_SOCKET
from logging_setup import configure_logging
from ui.standby import StandbyClock
from ui.menu import CRTMenu
from controls.keyboard import Keyboard
from controls.ir import IRController
class RetroTV:
    def __init__(self,base):
        self.base=Path(base); self.s=Settings(self.base/'config/settings.json'); self.s.load(); self.st=StateStore(self.base/'config/state.json'); self.st.load()
        self.log=configure_logging(Path(self.s.get('paths','logs'))/'retrotv.log'); self.lib=ChannelLibrary(self.s.get('paths','channels'),int(self.s.get('general','max_channels')),self.s.get('playback','supported_extensions'))
        self.p=MPVPlayer(MPV_SOCKET,self.log,self.s); self.clock=StandbyClock(self.p,self.s); self.menu=CRTMenu(self.s,self.p); self.ir=IRController(self.s,self.log)
        default_ch=int(self.s.get('general','default_channel'))
        saved_ch=int(self.st.get('current_channel',default_ch)) if self.s.get('general','remember_last_channel') else default_ch
        self.running=True; self.ch=saved_ch; self.vol=int(self.st.get('volume',self.s.get('audio','volume'))); self.muted=bool(self.st.get('muted',self.s.get('audio','muted'))); self.standby=False; self.gen=0
    def asset(self,c,n): return Path(self.s.get('paths','assets'))/c/n
    def effect(self,sound=None,video=None):
        for c,n in [('sounds',sound),('animations',video)]:
            if n:
                p=self.asset(c,n)
                if p.exists(): self.p.load(p); self.p.wait_end()
    def boot(self):
        self.p.start(); self.p.volume(self.vol); self.p.mute(self.muted); self.ir.start()
        if self.s.get('effects','startup_enabled'): self.effect('power_on.wav','startup.mp4')
        self.play_channel(self.ch)
    def play_channel(self,n):
        self.clock.stop(); self.standby=False; self.ch=self.lib.wrap(n); last=self.st.get('last_video_by_channel',{}); prev=last.get(str(self.ch))
        avoid_repeat=bool(self.s.get('playback','avoid_immediate_repeat'))
        v=self.lib.choose(self.ch,self.s.get('playback','mode'),prev,avoid_repeat)
        if not v and self.s.get('playback','skip_empty_channels'):
            for _ in range(self.lib.max_channels-1):
                self.ch=self.lib.wrap(self.ch+1)
                v=self.lib.choose(self.ch,self.s.get('playback','mode'),last.get(str(self.ch)),avoid_repeat)
                if v: break
        self.gen+=1; g=self.gen
        if not v:
            self.p.command('loadfile','av://lavfi:color=c=black:s=1280x720:r=1','replace'); self.p.show(f'CH {self.ch:02d}\nSIN SEÑAL',5000); return
        last[str(self.ch)]=str(v); self.st.set('last_video_by_channel',last); self.st.set('current_channel',self.ch); self.st.save(); self.p.load(v); self.p.show(f'CH {self.ch:02d}\n{self.lib.name(self.ch)}',2000)
        threading.Thread(target=self.monitor,args=(g,),daemon=True).start()
    def monitor(self,g):
        time.sleep(1)
        while self.running and g==self.gen and not self.standby:
            if self.p.prop('eof-reached') or self.p.prop('idle-active'):
                if g==self.gen and not self.standby:self.play_channel(self.ch)
                return
            time.sleep(.5)
    def change(self,d):
        if self.standby:return
        if self.s.get('effects','channel_change_enabled'):
            p=self.asset('animations','channel_change.mp4')
            if not p.exists(): p=self.asset('animations','static.mp4')
            if p.exists(): self.p.load(p); time.sleep(float(self.s.get('effects','static_duration_seconds')))
        self.play_channel(self.ch+d)
    def standby_toggle(self):
        if self.standby:
            self.standby=False; self.clock.stop(); self.effect('power_on.wav','startup.mp4'); self.play_channel(self.ch)
        else:
            self.gen+=1; self.standby=True; self.st.set('standby',True,save=True)
            if self.s.get('effects','shutdown_enabled'): self.effect('power_off.mp3','shutdown.mp4')
            self.clock.start()
    def key(self,k):
        if not k: return
        if self.menu.open:
            if k in ('m','ESC'): self.menu.toggle()
            elif k=='UP': self.menu.up()
            elif k=='DOWN': self.menu.down()
            elif k=='ENTER': self.menu.activate()
            return
        if k in ('n','RIGHT'): self.change(1)
        elif k in ('p','LEFT'): self.change(-1)
        elif k=='UP': self.vol=min(int(self.s.get('audio','max_volume')),self.vol+5); self.p.volume(self.vol); self.p.show(f'VOLUMEN {self.vol}')
        elif k=='DOWN': self.vol=max(0,self.vol-5); self.p.volume(self.vol); self.p.show(f'VOLUMEN {self.vol}')
        elif k=='m': self.menu.toggle()
        elif k=='SPACE': self.p.pause()
        elif k=='s': self.standby_toggle()
        elif k=='q': self.running=False
    def run(self):
        self.boot()
        with Keyboard() as kb:
            while self.running:
                k=kb.read()
                if k is None: time.sleep(.5); continue
                self.key(k)
        self.shutdown()
    def shutdown(self):
        self.running=False; self.gen+=1; self.clock.stop(); self.st.set('current_channel',self.ch); self.st.set('volume',self.vol); self.st.set('muted',self.muted); self.st.set('standby',self.standby); self.st.save(); self.ir.stop(); self.p.quit()
def lock():
    f=LOCK_FILE.open('w')
    try: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError: raise SystemExit('RetroTV ya está ejecutándose')
    f.write(str(os.getpid())); f.flush(); return f
def main():
    lk=lock(); app=RetroTV(os.environ.get('RETROTV_BASE','/home/retro/RetroTV'))
    signal.signal(signal.SIGTERM,lambda *_: setattr(app,'running',False)); signal.signal(signal.SIGINT,lambda *_: setattr(app,'running',False)); app.run()
if __name__=='__main__': main()
