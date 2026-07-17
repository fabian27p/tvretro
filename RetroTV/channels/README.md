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

Si no existe `channel.json`, RetroTV usa un nombre automatico. Si el canal tiene una sola subcarpeta, muestra el nombre de esa subcarpeta.
