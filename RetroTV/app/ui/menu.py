ITEMS=[('Modo','playback','mode'),('Recordar canal','general','remember_last_channel'),('Saltar vacíos','playback','skip_empty_channels'),('OSD','display','show_osd'),('IR','ir','enabled'),('GPIO IR BCM','ir','gpio_bcm'),('Reloj','standby','clock_format')]
class CRTMenu:
    def __init__(self,s,player): self.s=s; self.p=player; self.open=False; self.i=0
    def toggle(self): self.open=not self.open; self.render() if self.open else self.p.show('MENÚ CERRADO',1000)
    def render(self):
        ls=['RETROTV CONFIG']
        for j,(lab,a,b) in enumerate(ITEMS): ls.append(('> ' if j==self.i else '  ')+f'{lab}: {self.s.get(a,b)}')
        ls.append('\n↑/↓  ENTER  ESC'); self.p.show('\n'.join(ls),60000)
    def up(self): self.i=(self.i-1)%len(ITEMS); self.render()
    def down(self): self.i=(self.i+1)%len(ITEMS); self.render()
    def activate(self):
        _,a,b=ITEMS[self.i]; v=self.s.get(a,b)
        if isinstance(v,bool): v=not v
        elif (a,b)==('playback','mode'): v='sequential' if v=='random' else 'random'
        elif (a,b)==('standby','clock_format'): v='12h' if v=='24h' else '24h'
        elif (a,b)==('ir','gpio_bcm'): v=2 if int(v)>=27 else int(v)+1
        self.s.set(v,a,b); self.s.save(); self.render()
