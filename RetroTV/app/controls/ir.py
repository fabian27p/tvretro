class IRController:
    def __init__(self,settings,logger): self.s=settings; self.log=logger
    def start(self):
        if self.s.get('ir','enabled'): self.log.info('IR preparado en BCM GPIO%s; decodificación pendiente',self.s.get('ir','gpio_bcm'))
    def stop(self): pass
