# Assets

Estos archivos son opcionales. Si existen, RetroTV los usa automaticamente.

## Animaciones

```text
assets/animations/startup.mp4
assets/animations/shutdown.mp4
assets/animations/channel_change.mp4
assets/animations/static.mp4
```

- `startup.mp4`: se reproduce al encender la app.
- `shutdown.mp4`: se reproduce al entrar en standby.
- `channel_change.mp4`: se reproduce al cambiar de canal.
- `static.mp4`: respaldo si no existe `channel_change.mp4`.

## Sonidos

```text
assets/sounds/power_on.wav
assets/sounds/power_off.mp3
assets/sounds/channel_change.mp3
assets/sounds/static.mp3
assets/sounds/no_signal.mp3
assets/sounds/menu_open.mp3
assets/sounds/menu_move.mp3
assets/sounds/menu_select.mp3
assets/sounds/volume.mp3
```

- `power_on.wav`: sonido de encendido.
- `power_off.mp3`: sonido de apagado/standby.
- `channel_change.mp3`: ruido corto al cambiar de canal.
- `static.mp3`: ruido de estatica corto.
- `no_signal.mp3`: sonido para canal sin videos.
- `menu_open.mp3`, `menu_move.mp3`, `menu_select.mp3`: sonidos del menu.
- `volume.mp3`: beep de volumen.

## Recomendacion

Conviene guardar aqui solo animaciones y sonidos cortos. Para episodios o videos grandes, usa las carpetas `channels/channelXX/` directamente en la Raspberry o un disco USB.
