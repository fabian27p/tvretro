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
```

- `power_on.wav`: sonido de encendido.
- `power_off.mp3`: sonido de apagado/standby.

## Recomendacion

Conviene guardar aqui solo animaciones y sonidos cortos. Para episodios o videos grandes, usa las carpetas `channels/channelXX/` directamente en la Raspberry o un disco USB.
