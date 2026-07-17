import threading
from datetime import datetime
WEEKDAYS_ES=['LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO']
MONTHS_ES=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
class StandbyClock:
    def __init__(self,player,settings): self.p=player; self.s=settings; self.stop_evt=threading.Event(); self.th=None
    def start(self):
        self.stop(); self.stop_evt.clear(); self.p.command('loadfile','av://lavfi:color=c=black:s=1280x720:r=1','replace')
        self.th=threading.Thread(target=self.loop,daemon=True); self.th.start()
    def loop(self):
        while not self.stop_evt.is_set():
            if self.s.get('standby','show_clock'):
                t=self.text(datetime.now())
                self.p.show(t,1500,{
                    'font_size':self.s.get('standby','clock_font_size'),
                    'align_x':self.s.get('standby','clock_align_x'),
                    'align_y':self.s.get('standby','clock_align_y'),
                })
            self.stop_evt.wait(1)
    def text(self,now):
        fmt='%I:%M %p' if self.s.get('standby','clock_format')=='12h' else '%H:%M'
        lines=[now.strftime(fmt).lstrip('0')]
        if self.s.get('standby','show_weekday'):
            lines.append(WEEKDAYS_ES[now.weekday()])
        if self.s.get('standby','show_date'):
            if self.s.get('standby','date_style')=='calendar':
                lines.append(f'{now.day:02d} {MONTHS_ES[now.month-1]} {now.year}')
            else:
                lines.append(now.strftime('%d-%m-%Y'))
        msg=str(self.s.get('standby','standby_message',default='')).strip()
        if msg: lines.append(msg.upper())
        return '\n'.join(lines)
    def stop(self): self.stop_evt.set(); self.th.join(timeout=1) if self.th and self.th.is_alive() else None; self.th=None
