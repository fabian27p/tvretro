# Layout del control remoto

Control IR simple con numeros, `*`, `#`, flechas y `OK`.

## Mapa de uso RetroTV

```text
1-9     -> ir directo al canal 1-9
0       -> ir directo al canal 10
*       -> standby / volver desde menu
#       -> abrir o cerrar menu

Arriba  -> subir volumen / subir en menu
Abajo   -> bajar volumen / bajar en menu
Izq     -> canal anterior / bajar valor en menu
Der     -> canal siguiente / subir valor en menu
OK      -> pausa/play / aceptar en menu
```

Para canales 11 y 12 usa canal siguiente desde el 10, o cambia `max_channels` y el mapeo si luego usas otro control.

## IR

El receptor parte en BCM GPIO 6. Para aprender codigos reales del control, usa:

```bash
sudo ir-keytable -t
```

Luego mapea los eventos a acciones en `config/remote.json`.
