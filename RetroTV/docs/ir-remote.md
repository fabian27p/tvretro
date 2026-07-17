# Control remoto IR

RetroTV parte con receptor IR en **BCM GPIO 6**.

## Hardware

Conecta el receptor IR a:

```text
VCC  -> 3.3V
GND  -> GND
OUT  -> GPIO BCM 6
```

## Activar GPIO IR en Raspberry Pi OS

Editar `/boot/firmware/config.txt`:

```text
dtoverlay=gpio-ir,gpio_pin=6
```

Reiniciar:

```bash
sudo reboot
```

## Aprender teclas

Instalar herramientas:

```bash
sudo apt install -y ir-keytable
```

Ver eventos:

```bash
sudo ir-keytable -t
```

Presiona cada tecla del control y anota el nombre/codigo. Luego configura el mapa en:

```text
config/remote.json
```

Acciones esperadas por RetroTV:

```text
standby
channel_next
channel_prev
volume_up
volume_down
menu
enter
up
down
left
right
escape
pause
```

La decodificacion real depende del kernel (`gpio-ir`/`ir-keytable`). RetroTV mantiene la configuracion y acciones para que cualquier control pueda mapearse sin cambiar codigo.
