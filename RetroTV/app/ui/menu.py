ITEMS=[
    ('Modo reproduccion','playback','mode'),
    ('Recordar canal','general','remember_last_channel'),
    ('Saltar canales vacios','playback','skip_empty_channels'),
    ('OSD verde','display','show_osd'),
    ('Hora 12/24','standby','clock_format'),
    ('Mostrar fecha','standby','show_date'),
    ('Mostrar dia','standby','show_weekday'),
    ('Reloj en movimiento','standby','clock_motion'),
    ('Tamano reloj','standby','clock_font_size'),
    ('Probar volumen','action','volume_test'),
    ('Actualizar hora','action','update_clock'),
    ('Ajustar ano','clock_manual','year'),
    ('Ajustar mes','clock_manual','month'),
    ('Ajustar dia','clock_manual','day'),
    ('Ajustar hora','clock_manual','hour'),
    ('Ajustar minuto','clock_manual','minute'),
    ('Aplicar hora','action','set_manual_clock'),
    ('Config WiFi','action','wifi_info'),
    ('IR remoto','ir','enabled'),
    ('Aprender IR','ir','learn_enabled'),
    ('GPIO IR BCM','ir','gpio_bcm'),
]
class CRTMenu:
    def __init__(self,s,player,sound=None,actions=None): self.s=s; self.p=player; self.sound=sound; self.actions=actions or {}; self.open=False; self.i=0
    def beep(self,n):
        if self.sound: self.sound(n)
    def toggle(self): self.open=not self.open; self.render() if self.open else self.p.show('MENU CERRADO',1000,self.style())
    def style(self): return {'font_size':28,'align_x':'left','align_y':'top','margin_x':34,'margin_y':28}
    def render(self):
        ls=['RETROTV CONFIG']
        for j,(lab,a,b) in enumerate(ITEMS):
            marker='> ' if j==self.i else '  '
            ls.append(marker+f'{lab}: {self.value(a,b)}')
        ls.append('\nARRIBA/ABAJO  ENTER  ESC')
        self.p.show('\n'.join(ls),60000,self.style())
    def value(self,a,b):
        v=self.s.get(a,b)
        if isinstance(v,bool): return 'SI' if v else 'NO'
        return str(v)
    def up(self): self.i=(self.i-1)%len(ITEMS); self.beep('menu_move.mp3'); self.render()
    def down(self): self.i=(self.i+1)%len(ITEMS); self.beep('menu_move.mp3'); self.render()
    def left(self): self.adjust(-1)
    def right(self): self.adjust(1)
    def adjust(self,delta):
        self.beep('menu_select.mp3')
        _,a,b=ITEMS[self.i]; v=self.s.get(a,b)
        if a=='clock_manual':
            v=self.step_clock_field(b,int(v),delta); self.s.set(v,a,b); self.s.save(); self.render(); return
        if delta<0: return
        self.activate_current(a,b,v)
    def activate(self):
        self.beep('menu_select.mp3')
        _,a,b=ITEMS[self.i]; v=self.s.get(a,b)
        self.activate_current(a,b,v)
    def activate_current(self,a,b,v):
        if a=='action':
            if b=='volume_test':
                self.beep('volume.mp3'); self.p.show('PRUEBA VOLUMEN\n[###############-----]',1200,self.style())
            elif b=='update_clock':
                action=self.actions.get('update_clock')
                ok,msg=action() if action else (False,'HORA\nAccion no disponible')
                self.p.show(msg,5000,self.style())
            elif b=='set_manual_clock':
                action=self.actions.get('set_manual_clock')
                ok,msg=action(self.s.get('clock_manual')) if action else (False,'HORA\nAccion no disponible')
                self.p.show(msg,5000,self.style())
            elif b=='wifi_info':
                self.p.show('WIFI\nUsar Raspberry Pi Imager, raspi-config, nmtui o nmcli',5000,self.style())
            return
        if isinstance(v,bool): v=not v
        elif (a,b)==('playback','mode'):
            modes=self.s.get('playback','modes',default=['random','sequential','daily','resume'])
            v=modes[(modes.index(v)+1)%len(modes)] if v in modes else modes[0]
        elif (a,b)==('standby','clock_format'): v='12h' if v=='24h' else '24h'
        elif (a,b)==('standby','clock_font_size'): v=52 if int(v)>=84 else int(v)+8
        elif (a,b)==('ir','gpio_bcm'): v=2 if int(v)>=27 else int(v)+1
        self.s.set(v,a,b); self.s.save(); self.render()
    def step_clock_field(self,field,value,delta):
        limits={'year':(2024,2035),'month':(1,12),'day':(1,31),'hour':(0,23),'minute':(0,59)}
        lo,hi=limits[field]; value+=delta
        if value>hi: value=lo
        if value<lo: value=hi
        return value
