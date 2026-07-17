# RetroTV 0.1.0

Primera versión funcional para Raspberry Pi OS Lite.

## Incluye
- MPV persistente por IPC
- startup
- 12 canales
- reproducción aleatoria/secuencial
- OSD
- standby con reloj
- menú CRT básico
- GPIO IR configurable (decodificación IR pendiente)
- estado persistente
- servicio systemd
- instalador y respaldo

## Instalación
Copia `app`, `config`, `tools`, `systemd` y este README dentro de `/home/retro/RetroTV/`. No borres `assets` ni `channels`.

```bash
cd /home/retro/RetroTV
chmod +x tools/*.sh
./tools/install.sh
sudo pkill mpv || true
python3 /home/retro/RetroTV/app/main.py
```

## Controles
- N/flecha derecha: canal siguiente
- P/flecha izquierda: canal anterior
- flecha arriba/abajo: volumen
- M: menú
- Enter: cambiar opción
- Escape: cerrar menú
- Espacio: pausa
- S: standby
- Q: salir

## Servicio (solo después de probar)
```bash
sudo systemctl enable --now retrotv
```

Para desactivar:
```bash
sudo systemctl disable --now retrotv
```

El IR queda configurado en `config/settings.json`, inicialmente BCM GPIO6 (pin físico 31).
