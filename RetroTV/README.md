# RetroTV 0.1.1

Aplicacion Python ligera para crear una TV retro generica en Raspberry Pi OS Lite. Arranca `mpv`, reproduce videos por canales y puede quedar corriendo como servicio `systemd`.

## Objetivo

- Reproducir videos de forma continua.
- Simular canales con carpetas separadas.
- Permitir que cada canal tenga cualquier serie, pelicula o coleccion.
- Encender directo a pantalla completa.
- Funcionar bien en Raspberry Pi OS Lite o una distro Linux compatible.

## Estructura

```text
RetroTV/
  app/                 Codigo de la aplicacion
  assets/
    animations/        startup.mp4, shutdown.mp4, static.mp4, channel_change.mp4
    sounds/            power_on.wav, power_off.mp3
  channels/
    README.md          Guia para cargar contenido
    channel01/         Videos del canal 1
    channel02/         Videos del canal 2
  config/
    settings.json      Configuracion principal
    state.json         Estado persistente
  systemd/
    retrotv.service
  tools/
    install.sh
    backup_retrotv.sh
```

## Instalacion en Raspberry Pi OS Lite

Crear usuario recomendado:

```bash
sudo useradd -m -s /bin/bash retro
sudo mkdir -p /home/retro
sudo chown retro:retro /home/retro
```

### Desde GitHub

Instalar dependencias base:

```bash
sudo apt update
sudo apt install -y git
```

Clonar el repo fuente:

```bash
sudo -u retro git clone https://github.com/fabian27p/tvretro.git /home/retro/tvretro-src
```

Si el repo es privado, usa SSH o un token de GitHub en lugar de la URL publica.

Instalar RetroTV:

```bash
cd /home/retro/tvretro-src/RetroTV
chmod +x tools/*.sh
./tools/install.sh
```

El instalador copia la app al destino final:

```text
/home/retro/RetroTV
```

### Copia manual

Tambien puedes copiar este directorio a:

```text
/home/retro/RetroTV
```

Instalar dependencias:

```bash
cd /home/retro/RetroTV
chmod +x tools/*.sh
./tools/install.sh
```

Probar manualmente:

```bash
python3 /home/retro/RetroTV/app/main.py
```

Activar arranque automatico:

```bash
sudo systemctl enable --now retrotv
```

Ver logs:

```bash
journalctl -u retrotv -f
tail -f /home/retro/RetroTV/logs/retrotv.log
```

## Canales

Pon los videos dentro de las carpetas:

```text
channels/channel01/
channels/channel02/
channels/channel03/
```

Cada canal es generico. Puedes organizarlo como prefieras:

```text
channels/channel01/Mi Serie/S01E01.mp4
channels/channel01/Mi Serie/S01E02.mp4
channels/channel02/Otra Coleccion/video-001.mp4
```

Opcionalmente crea un `channel.json` dentro de cada canal:

```json
{
  "name": "Canal Animacion"
}
```

Ese nombre se muestra en pantalla al cambiar de canal.

Extensiones soportadas por defecto:

- `.mp4`
- `.mkv`
- `.m4v`
- `.mov`

Para una pantalla pequena conviene usar H.264 + AAC en 480p o 720p.

## Assets de inicio

Puedes agregar al repositorio los videos y sonidos cortos de la experiencia retro:

```text
assets/animations/startup.mp4
assets/animations/shutdown.mp4
assets/animations/channel_change.mp4
assets/animations/static.mp4
assets/sounds/power_on.wav
assets/sounds/power_off.mp3
```

RetroTV los detecta automaticamente. Si no existen, simplemente los salta.

Para mantener el repo rapido, deja aqui solo clips cortos. Los episodios o bibliotecas grandes conviene copiarlos despues a `channels/` en la Raspberry, o montarlos desde un USB/SSD.

## Controles de teclado

- `N` o flecha derecha: canal siguiente
- `P` o flecha izquierda: canal anterior
- flecha arriba/abajo: volumen
- `M`: menu
- `Enter`: cambiar opcion del menu
- `Escape`: cerrar menu
- espacio: pausa
- `S`: standby
- `Q`: salir

Cuando corre como servicio no hay teclado conectado a stdin; la app sigue reproduciendo y queda lista para control IR futuro.

El menu permite cambiar modo de reproduccion, OSD, fecha/hora, movimiento del reloj standby, IR y GPIO BCM del receptor remoto.

Modos de reproduccion:

- `random`: episodio aleatorio del canal.
- `sequential`: sigue el orden de archivos.
- `daily`: un capitulo fijo por canal cada dia.
- `resume`: vuelve al ultimo video y posicion guardada del canal.

Hora/WiFi: el menu incluye `Actualizar hora`, pensado para sincronizar el reloj por NTP si la Raspberry tiene red. Si no instalas pila RTC, tambien puedes ajustar ano, mes, dia, hora y minuto manualmente desde el menu y usar `Aplicar hora`. En los campos de hora manual, `Enter`/derecha sube y izquierda baja. Para configurar WiFi en Raspberry Pi OS Lite conviene usar Raspberry Pi Imager, `raspi-config`, `nmtui` o `nmcli`; escribir SSID/password con control remoto es incomodo y poco seguro.

IR: ver [docs/ir-remote.md](docs/ir-remote.md) y [docs/remote-layout.md](docs/remote-layout.md). Por defecto usa BCM GPIO 6.

## Configuracion de video

En `config/settings.json`:

```json
"mpv": {
  "video_output": "drm",
  "hwdec": "auto-safe",
  "extra_args": []
}
```

Para Raspberry Pi OS Lite usa `drm`.

Para probar en escritorio, cambia temporalmente a:

```json
"video_output": "auto"
```

## Estilo CRT

El texto en pantalla usa verde fluorescente por defecto:

```json
"display": {
  "osd_color": "#FF39FF14",
  "osd_font_size": 36
}
```

El reloj de standby se muestra grande y centrado:

```json
"standby": {
  "show_date": true,
  "show_weekday": true,
  "date_style": "calendar",
  "standby_message": "",
  "clock_font_size": 76,
  "clock_safe_margin_x": 110,
  "clock_safe_margin_y": 78,
  "clock_align_x": "center",
  "clock_align_y": "center"
}
```

La fecha usa la hora local del sistema, asi que no necesita internet. Si quieres mostrar una frase bajo la fecha, puedes usar `standby_message`, por ejemplo `"standby_message": "MODO ESCRITORIO"`.

El OSD de canal aparece arriba a la derecha. El volumen aparece abajo con una barra verde. En standby, el reloj/calendario usa gris tenue y se desplaza cada pocos segundos dentro de un area segura para no pegarse a las esquinas redondeadas de una pantalla CRT.

## Placa Allwinner H616 / IK316-EMCP

Este proyecto no es Android; es una alternativa Linux ligera. Para usarlo en la placa H616 necesitas una imagen Linux que ya tenga salida HDMI, audio y aceleracion o decodificacion suficiente para `mpv`.

Ruta recomendada:

1. Conseguir/respaldar firmware original de la placa.
2. Probar una imagen Linux compatible H616.
3. Instalar `mpv` y Python 3.
4. Copiar RetroTV a `/home/retro/RetroTV`.
5. Ajustar `config/settings.json` si `--gpu-context=drm` no funciona.

Con 1GB de RAM, esta ruta suele ser mas razonable que un Android completo.
