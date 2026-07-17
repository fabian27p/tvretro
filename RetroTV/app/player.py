import json,socket,subprocess,time
from pathlib import Path
class MPVPlayer:
    def __init__(self,socket_path,logger): self.socket_path=Path(socket_path); self.logger=logger; self.process=None; self.req=0
    def start(self):
        self.quit(); self.socket_path.unlink(missing_ok=True)
        cmd=['mpv','--idle=yes','--fullscreen=yes','--no-terminal','--really-quiet','--keep-open=yes','--input-ipc-server='+str(self.socket_path),'--vo=gpu','--gpu-context=drm','--hwdec=auto-safe','--no-osc','--no-input-default-bindings']
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
    def load(self,p): self.command('loadfile',str(p),'replace')
    def show(self,t,ms=2000): self.command('show-text',t,ms)
    def volume(self,v): self.command('set_property','volume',v)
    def mute(self,m): self.command('set_property','mute','yes' if m else 'no')
    def pause(self): self.command('cycle','pause')
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
