# RetroTV

Proyecto para crear una TV retro generica en Raspberry Pi OS Lite.

La aplicacion vive en [`RetroTV/`](RetroTV/) y usa Python + `mpv` para reproducir videos por canales, mostrar animaciones de inicio/cambio y dejar una pantalla standby tipo reloj/calendario CRT.

## Instalacion rapida

```bash
sudo apt update
sudo apt install -y git
sudo useradd -m -s /bin/bash retro
sudo -u retro git clone https://github.com/fabian27p/tvretro.git /home/retro/tvretro-src
cd /home/retro/tvretro-src/RetroTV
chmod +x tools/*.sh
./tools/install.sh
sudo systemctl enable --now retrotv
```

Los episodios o videos grandes no van en el repo. Copialos aparte en:

```text
/home/retro/RetroTV/channels/channel01/
/home/retro/RetroTV/channels/channel02/
```
