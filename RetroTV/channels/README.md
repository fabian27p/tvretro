# Canales

Cada carpeta `channelXX` representa un canal. Puedes poner cualquier serie, pelicula o coleccion de videos dentro.

Ejemplo:

```text
channels/
  channel01/
    channel.json
    Serie A/
      S01E01.mp4
      S01E02.mp4
  channel02/
    channel.json
    Dibujos/
      episodio-001.mkv
```

El archivo `channel.json` es opcional. Sirve para definir el nombre que aparece en pantalla:

```json
{
  "name": "Canal Familiar"
}
```

Tambien puede apuntar a una carpeta externa, util para probar en el PC o usar un disco USB:

```json
{
  "name": "Canal Familiar",
  "path": "/Users/tu-usuario/Videos/Canal Familiar"
}
```

Si la ruta es personal de tu computador, usa `channel.local.json`. RetroTV lo lee primero y Git lo ignora para no publicar rutas locales:

```json
{
  "name": "Canal Local",
  "path": "/Users/tu-usuario/Movies/Series"
}
```

En Raspberry, un disco USB podria quedar asi:

```json
{
  "name": "Dibujos",
  "path": "/media/retro/USB/Dibujos"
}
```

Si no existe `channel.json`, RetroTV usa un nombre automatico. Si el canal tiene una sola subcarpeta, muestra el nombre de esa subcarpeta.
