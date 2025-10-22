### Scripts

En este directorio se encuentra un script (`restart_server.sh`) que nos servirá para levantar tmux con un archivo de configuración personalizado (incluido en este directorio) y una vez dentro de una ventana de la sesión tmux, ejecutará los comandos necesarios para poner el servicio de FastAPI en línea.

Se incluyen algunos archivos de configuración:
- `uvicorn-log.yaml`
- `uvicorn-sia-log-config.yaml`
Para cambiar el formato de la salida de uvicorn.

Por último, se incluye un archivo plantilla para la creación de un servicio (`fastapi-sia-server.service.template`) que debería ejecutarse automáticamente luego del reinicio del servidor. Cuando ese servicio se ejecute, el script `restar_server.sh` volverá a dejar a la API en funcionamiento.

**Importante**: El archivo plantilla debe ser modificado y correctamente copiado al directorio adecuado para que systemd pueda encontrarlo. También deberá ser habilitado (`systemctl enable`) y activado (`systemctl activate`) para que pueda ejecutarse como servicio.
