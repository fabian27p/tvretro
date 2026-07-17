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
    ('IR remoto','ir','enabled'),
    ('GPIO IR BCM','ir','gpio_bcm'),
]
class CRTMenu:
    def __init__(self,s,player): self.s=s; self.p=player; self.open=False; self.i=0
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
    def up(self): self.i=(self.i-1)%len(ITEMS); self.render()
    def down(self): self.i=(self.i+1)%len(ITEMS); self.render()
    def activate(self):
        _,a,b=ITEMS[self.i]; v=self.s.get(a,b)
        if isinstance(v,bool): v=not v
        elif (a,b)==('playback','mode'): v='sequential' if v=='random' else 'random'
        elif (a,b)==('standby','clock_format'): v='12h' if v=='24h' else '24h'
        elif (a,b)==('standby','clock_font_size'): v=52 if int(v)>=84 else int(v)+8
        elif (a,b)==('ir','gpio_bcm'): v=2 if int(v)>=27 else int(v)+1
        self.s.set(v,a,b); self.s.save(); self.render()
