import sys,termios,tty
class Keyboard:
    def __enter__(self):
        self.fd=sys.stdin.fileno(); self.old=termios.tcgetattr(self.fd) if sys.stdin.isatty() else None
        if self.old: tty.setcbreak(self.fd)
        return self
    def __exit__(self,*a):
        if self.old: termios.tcsetattr(self.fd,termios.TCSADRAIN,self.old)
    def read(self):
        c=sys.stdin.read(1)
        if c=='\x1b':
            n=sys.stdin.read(1)
            if n=='[': return {'A':'UP','B':'DOWN','C':'RIGHT','D':'LEFT'}.get(sys.stdin.read(1),'ESC')
            return 'ESC'
        if c in ('\r','\n'): return 'ENTER'
        if c==' ': return 'SPACE'
        return c.lower()
