# Configuracion del Servidor

## Orden de Prioridad

1. **Flag CLI**: `onyxlog-tui --url http://...`
2. **Variable de entorno**: `ONYXLOG_URL`
3. **Archivo de config**: `~/.onyxlog/config.toml` con clave `server.url`

## Default

`http://localhost:8000`

## Archivo de Config

- Ubicacion: `~/.onyxlog/config.toml`
- Se crea automaticamente en el primer uso
- Formato TOML:

```toml
[server]
url = "http://localhost:8000"
```

## Implementacion

La logica de configuracion esta en `src/config.py` con la clase `Settings` que:
- Lee la URL del servidor en el orden de prioridad indicado
- Crea el directorio `~/.onyxlog/` si no existe
- Crea el archivo `config.toml` con valores default si no existe
- Permite actualizar la URL del servidor en runtime