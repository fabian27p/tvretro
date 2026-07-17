from __future__ import annotations
import fcntl,os,signal,sys,threading,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from config import Settings
from state import StateStore
from channels import ChannelLibrary
from player import MPVPlayer
from constants import KEY_FIFO,LOCK_FILE,MPV_INPUT_CONF,MPV_SOCKET
from logging_setup import configure_logging
from ui.standby import StandbyClock
from ui.menu import CRTMenu
from controls.keyboard import Keyboard
from controls.ir import IRController
from system_actions import set_manual_clock,update_clock
class RetroTV:
    def __init__(self,base):
        self.base=Path(base); self.s=Settings(self.base/'config/settings.json'); self.s.load(); self.st=StateStore(self.base/'config/state.json'); self.st.load()
        self.log=configure_logging(Path(self.s.get('paths','logs'))/'retrotv.log'); self.lib=ChannelLibrary(self.s.get('paths','channels'),int(self.s.get('general','max_channels')),self.s.get('playback','supported_extensions'))
        self.p=MPVPlayer(MPV_SOCKET,self.log,self.s,KEY_FIFO,MPV_INPUT_CONF); self.clock=StandbyClock(self.p,self.s); self.menu=CRTMenu(self.s,self.p,self.sound,{'update_clock':update_clock,'set_manual_clock':set_manual_clock}); self.ir=IRController(self.s,self.log)
        default_ch=int(self.s.get('general','default_channel'))
        saved_ch=int(self.st.get('current_channel',default_ch)) if self.s.get('general','remember_last_channel') else default_ch
        self.running=True; self.ch=saved_ch; self.vol=int(self.st.get('volume',self.s.get('audio','volume'))); self.muted=bool(self.st.get('muted',self.s.get('audio','muted'))); self.standby=False; self.gen=0
    def asset(self,c,n): return Path(self.s.get('paths','assets'))/c/n
    def effect(self,sound=None,video=None):
        for c,n in [('sounds',sound),('animations',video)]:
            if n:
                p=self.asset(c,n)
                if p.exists(): self.p.load(p); self.p.wait_end()
    def sound(self,n):
        p=self.asset('sounds',n)
        if p.exists(): self.p.sound(p)
    def boot(self):
        self.p.start(); self.p.volume(self.vol); self.p.mute(self.muted); self.ir.start()
        if self.s.get('effects','startup_enabled'): self.effect('power_on.wav','startup.mp4')
        self.play_channel(self.ch)
    def channel_style(self):
        return {'font_size':self.s.get('display','channel_font_size',default=30),'align_x':'right','align_y':'top','margin_x':28,'margin_y':24}
    def volume_style(self):
        return {'font_size':self.s.get('display','volume_font_size',default=34),'align_x':'center','align_y':'bottom','margin_x':20,'margin_y':54}
    def volume_text(self):
        width=20; filled=round(width*self.vol/max(1,int(self.s.get('audio','max_volume'))))
        return f'VOLUMEN {self.vol:03d}\n[{"#"*filled}{"-"*(width-filled)}]'
    def no_signal_animation(self):
        for name in ('no_signal.mp4','static.mp4','channel_change.mp4'):
            p=self.asset('animations',name)
            if p.exists(): return p
        return None
    def play_channel(self,n):
        self.clock.stop(); self.standby=False; self.ch=self.lib.wrap(n); last=self.st.get('last_video_by_channel',{}); prev=last.get(str(self.ch))
        avoid_repeat=bool(self.s.get('playback','avoid_immediate_repeat'))
        mode=self.s.get('playback','mode')
        resume=(self.st.get('resume_by_channel',{}) or {}).get(str(self.ch))
        v=self.lib.choose(self.ch,mode,prev,avoid_repeat,resume)
        if not v and self.s.get('playback','skip_empty_channels'):
            for _ in range(self.lib.max_channels-1):
                self.ch=self.lib.wrap(self.ch+1)
                resume=(self.st.get('resume_by_channel',{}) or {}).get(str(self.ch))
                v=self.lib.choose(self.ch,mode,last.get(str(self.ch)),avoid_repeat,resume)
                if v: break
        self.gen+=1; g=self.gen
        if not v:
            anim=self.no_signal_animation()
            if anim: self.p.load(anim,loop=True)
            else: self.p.command('loadfile','av://lavfi:color=c=black:s=1280x720:r=1','replace'); self.p.command('set_property','pause',False)
            self.sound('no_signal.mp3'); self.p.show(f'CH {self.ch:02d}\nSIN SEÑAL',60000,self.channel_style()); return
        last[str(self.ch)]=str(v); self.st.set('last_video_by_channel',last); self.st.set('current_channel',self.ch); self.st.save(); self.p.load(v)
        if mode=='resume' and resume and resume.get('path')==str(v) and float(resume.get('time',0))>5:
            self.p.seek(max(0,float(resume.get('time',0))-2))
        self.p.show(f'CH {self.ch:02d}\n{self.lib.name(self.ch)}',2000,self.channel_style())
        threading.Thread(target=self.monitor,args=(g,),daemon=True).start()
    def monitor(self,g):
        time.sleep(1)
        ticks=0
        while self.running and g==self.gen and not self.standby:
            ticks+=1
            if ticks%4==0: self.save_resume()
            if self.p.prop('eof-reached') or self.p.prop('idle-active'):
                self.clear_resume()
                if g==self.gen and not self.standby:self.play_channel(self.ch)
                return
            time.sleep(.5)
    def save_resume(self):
        path=self.p.prop('path'); pos=self.p.prop('time-pos')
        if not path or pos is None: return
        resume=self.st.get('resume_by_channel',{}) or {}
        resume[str(self.ch)]={'path':str(path),'time':float(pos),'updated_at':int(time.time())}
        self.st.set('resume_by_channel',resume); self.st.save()
    def clear_resume(self):
        resume=self.st.get('resume_by_channel',{}) or {}
        if str(self.ch) in resume:
            resume.pop(str(self.ch),None); self.st.set('resume_by_channel',resume); self.st.save()
    def change(self,d):
        if self.standby:return
        if self.s.get('effects','channel_change_enabled'):
            self.sound('channel_change.mp3')
            p=self.asset('animations','channel_change.mp4')
            if not p.exists(): p=self.asset('animations','static.mp4')
            if p.exists(): self.p.load(p); time.sleep(float(self.s.get('effects','static_duration_seconds')))
        self.play_channel(self.ch+d)
    def standby_toggle(self):
        if self.standby:
            self.standby=False; self.st.set('standby',False,save=True); self.clock.stop()
            if self.s.get('effects','startup_enabled'): self.effect('power_on.wav','startup.mp4')
            self.play_channel(self.ch)
        else:
            self.gen+=1; self.standby=True; self.st.set('standby',True,save=True)
            if self.s.get('effects','shutdown_enabled'): self.effect('power_off.mp3','shutdown.mp4')
            self.clock.start()
    def key(self,k):
        if not k: return
        if self.standby and k not in ('q','m','#','ESC'):
            self.standby_toggle(); return
        if self.menu.open:
            if k in ('m','#','*','ESC'): self.menu.toggle()
            elif k=='UP': self.menu.up()
            elif k=='DOWN': self.menu.down()
            elif k=='LEFT': self.menu.left()
            elif k=='RIGHT': self.menu.right()
            elif k in ('ENTER','OK'): self.menu.activate()
            return
        if k.isdigit(): self.goto_channel(10 if k=='0' else int(k))
        elif k in ('n','RIGHT'): self.change(1)
        elif k in ('p','LEFT'): self.change(-1)
        elif k=='UP': self.vol=min(int(self.s.get('audio','max_volume')),self.vol+5); self.p.volume(self.vol); self.sound('volume.mp3'); self.p.show(self.volume_text(),1000,self.volume_style())
        elif k=='DOWN': self.vol=max(0,self.vol-5); self.p.volume(self.vol); self.sound('volume.mp3'); self.p.show(self.volume_text(),1000,self.volume_style())
        elif k in ('m','#'): self.sound('menu_open.mp3'); self.menu.toggle()
        elif k in ('SPACE','ENTER','OK'): self.p.pause()
        elif k in ('s','*'): self.standby_toggle()
        elif k=='q': self.running=False
    def goto_channel(self,n):
        if n<1 or n>int(self.s.get('general','max_channels')): return
        self.play_channel(n)
    def run(self):
        with Keyboard(KEY_FIFO) as kb:
            self.boot()
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
