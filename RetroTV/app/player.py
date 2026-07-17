import json,socket,subprocess,time
from pathlib import Path
class MPVPlayer:
    def __init__(self,socket_path,logger,settings=None,key_fifo_path=None,input_conf_path=None):
        self.socket_path=Path(socket_path); self.logger=logger; self.settings=settings; self.key_fifo_path=Path(key_fifo_path) if key_fifo_path else None; self.input_conf_path=Path(input_conf_path) if input_conf_path else None; self.process=None; self.req=0
    def write_input_conf(self):
        if not self.key_fifo_path or not self.input_conf_path: return None
        bindings={
            'n':'n','p':'p','RIGHT':'RIGHT','LEFT':'LEFT','UP':'UP','DOWN':'DOWN',
            'm':'m','ENTER':'ENTER','ESC':'ESC','SPACE':'SPACE','s':'s','q':'q',
            'N':'n','P':'p','M':'m','S':'s','Q':'q','#':'#','*':'*',
            '0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9'
        }
        lines=[]
        fifo=str(self.key_fifo_path)
        for key,token in bindings.items():
            lines.append(f"{key} run \"/bin/sh\" \"-c\" \"printf '%s\\\\n' {token!r} > {fifo!r}\"")
        self.input_conf_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        return self.input_conf_path
    def build_cmd(self):
        vo=(self.settings.get('mpv','video_output',default='drm') if self.settings else 'drm')
        hwdec=(self.settings.get('mpv','hwdec',default='auto-safe') if self.settings else 'auto-safe')
        cmd=['mpv','--idle=yes','--fullscreen=yes','--no-terminal','--really-quiet','--keep-open=yes','--input-ipc-server='+str(self.socket_path),'--no-osc','--no-input-default-bindings']
        input_conf=self.write_input_conf()
        if input_conf: cmd+=['--input-conf='+str(input_conf)]
        if vo=='drm':
            cmd+=['--vo=gpu','--gpu-context=drm']
        elif vo and vo!='auto':
            cmd+=['--vo='+str(vo)]
        if hwdec and hwdec!='off':
            cmd+=['--hwdec='+str(hwdec)]
        cmd+=list(self.settings.get('mpv','extra_args',default=[]) if self.settings else [])
        return cmd
    def start(self):
        self.quit(); self.socket_path.unlink(missing_ok=True)
        cmd=self.build_cmd()
        self.process=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        for _ in range(100):
            if self.socket_path.exists(): return
            time.sleep(.05)
        raise RuntimeError('MPV no creó socket IPC')
    def command(self,*parts,reply=False):
        if not self.process or self.process.poll() is not None: self.start()
        self.req+=1; data=(json.dumps({'command':list(parts),'request_id':self.req})+'\n').encode()
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
            s.settimeout(2); s.connect(str(self.socket_path)); s.sendall(data)
            if not reply: return None
            raw=b''
            while b'\n' not in raw:
                c=s.recv(65536)
                if not c: break
                raw+=c
            return json.loads(raw.splitlines()[0].decode()) if raw else None
    def load(self,p,loop=False):
        self.command('set_property','loop-file','inf' if loop else 'no')
        self.command('loadfile',str(p),'replace')
        self.command('set_property','pause',False)
    def sound(self,p):
        self.command('audio-add',str(p),'auto')
    def apply_osd_style(self,style=None):
        if not self.settings: return
        style=style or {}
        props={
            'osd-color':style.get('color',self.settings.get('display','osd_color',default='#FF39FF14')),
            'osd-border-color':style.get('border_color',self.settings.get('display','osd_border_color',default='#FF003300')),
            'osd-font-size':style.get('font_size',self.settings.get('display','osd_font_size',default=36)),
            'osd-align-x':style.get('align_x',self.settings.get('display','osd_align_x',default='center')),
            'osd-align-y':style.get('align_y',self.settings.get('display','osd_align_y',default='top')),
            'osd-margin-x':style.get('margin_x',20),
            'osd-margin-y':style.get('margin_y',20),
        }
        for k,v in props.items(): self.command('set_property',k,v)
    def show(self,t,ms=2000,style=None):
        if self.settings and not self.settings.get('display','show_osd',default=True): return
        self.apply_osd_style(style)
        self.command('show-text',t,ms)
    def volume(self,v): self.command('set_property','volume',v)
    def mute(self,m): self.command('set_property','mute','yes' if m else 'no')
    def pause(self): self.command('cycle','pause')
    def seek(self,seconds): self.command('set_property','time-pos',float(seconds))
    def prop(self,n):
        r=self.command('get_property',n,reply=True); return r.get('data') if r and r.get('error')=='success' else None
    def wait_end(self):
        time.sleep(.3)
        while True:
            if self.prop('eof-reached') or self.prop('idle-active'): return
            time.sleep(.2)
    def quit(self):
        if self.process and self.process.poll() is None:
            try:self.command('quit')
            except Exception: pass
            try:self.process.wait(timeout=3)
            except Exception:self.process.kill()
        self.process=None; self.socket_path.unlink(missing_ok=True)
