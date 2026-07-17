import os,select,sys,termios,tty
class Keyboard:
    def __init__(self,fifo_path=None): self.fifo_path=fifo_path; self.fifo_fd=None; self.buf=b''
    def __enter__(self):
        self.fd=sys.stdin.fileno(); self.old=termios.tcgetattr(self.fd) if sys.stdin.isatty() else None
        if self.old: tty.setcbreak(self.fd)
        if self.fifo_path:
            try:
                if os.path.exists(self.fifo_path): os.unlink(self.fifo_path)
                os.mkfifo(self.fifo_path,0o600)
                self.fifo_fd=os.open(self.fifo_path,os.O_RDWR|os.O_NONBLOCK)
            except Exception:
                self.fifo_fd=None
        return self
    def __exit__(self,*a):
        if self.old: termios.tcsetattr(self.fd,termios.TCSADRAIN,self.old)
        if self.fifo_fd is not None:
            os.close(self.fifo_fd); self.fifo_fd=None
        if self.fifo_path and os.path.exists(self.fifo_path):
            try: os.unlink(self.fifo_path)
            except Exception: pass
    def read_fifo(self):
        if self.fifo_fd is None: return None
        ready,_,_=select.select([self.fifo_fd],[],[],0)
        if not ready: return None
        try: self.buf+=os.read(self.fifo_fd,1024)
        except BlockingIOError: return None
        if b'\n' not in self.buf: return None
        line,self.buf=self.buf.split(b'\n',1)
        return line.decode(errors='ignore')
    def read(self):
        k=self.read_fifo()
        if k: return k
        if not sys.stdin.isatty(): return None
        ready,_,_=select.select([sys.stdin],[],[],0.5)
        if not ready: return None
        c=sys.stdin.read(1)
        if c=='\x1b':
            n=sys.stdin.read(1)
            if n=='[': return {'A':'UP','B':'DOWN','C':'RIGHT','D':'LEFT'}.get(sys.stdin.read(1),'ESC')
            return 'ESC'
        if c in ('\r','\n'): return 'ENTER'
        if c==' ': return 'SPACE'
        return c.lower()
