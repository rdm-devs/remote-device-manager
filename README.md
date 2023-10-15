# fastapi-sia-test

**Disclaimer**: Este es un proyecto en construcción por lo que es posible que se encuentren errores.

## ¿Cómo ejecutar el proyecto?

1. Habiendo creado un entorno virtual, procedemos con la instalación de las dependencias: `pip install -r requirements.txt`.
2. Creamos un archivo llamado `.env`, modificando los valores indicados en el archivo plantilla `.env.template` según corresponda. 
   En entornos de desarrollo `ROOT_PATH_DEV` debe ser `""` mientras que en producción el valor de `ROOT_PATH_PROD` dependerá de como haya sido configurado el proxy ya que la ruta principal de la api puede no estar en `https://<my_domain>/` sino bajo otra ruta, por ejemplo: `https://<my_domain>/api/`. Adicionalmente, configuramos el valor de la cadena de conexión a la base de datos  de desarrollo `DB_CONNECTION_DEV` con el valor correpondiente según el motor de base de datos utilizado. Ver **observaciones** más abajo.
3. Ejecutamos `export ENV=DEV` y lanzamos la aplicación FastAPI desde el directorio raíz: `uvicorn src.main:app --reload`. 
   Es importante el primer comando ya que la aplicación cargará diferentes valores dependiendo del tipo de entorno de trabajo, `ENV=DEV` para desarrollo y `ENV=PROD` para producción.
4. Accedemos a la documentación de la API para empezar a probar los endpoints disponibles: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

**Observaciones**

Una base de datos se creará automáticamente en el directorio indicado en el archivo `.env` bajo la variable `DB_CONNECTION_DEV`. Por ejemplo un valor valido puede ser `sqlite:///.fastpi-sia.db`, lo cual crearía la base de datos `fastapi-sia.db` en el directorio raíz del proyecto. Para ver su contenido, se puede utilizar el programa [DB Browser for SQLite](https://sqlitebrowser.org/dl/), disponible para Windows, Mac y Linux.

La estructura del proyecto está basada en estas recomendaciones: [fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices).

## Cómo ejecutar en producción

**Importante:** Configurar debidamente los valores del archivo `.env`. 

### Manualmente

Ubicados en la carpeta raíz del proyecto `fastapi-sia-test`, ejecutamos `export ENV=PROD` y luego procedemos con alguna de las siguientes alternativas:
 
1. Con `uvicorn`: `uvicorn src.main:app --host 0.0.0.0 --port 5000`
2. Con `gunicorn`: `gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 src.main:app`

### Automáticamente

Opcionalmente puede crearse un archivo de servicio del sistema, a ejecutar mediante `systemctl`. Por ejemplo, el archivo `/etc/systemd/system/fastapi-sia-test.service`:

```conf
[Unit]
Description=Gunicorn instance to serve FastAPI SIA app
After=network.target

[Service]
User=<username>
Group=www-data
WorkingDirectory=</absolute/path/to/repo>
Environment="PATH=</absolute/path/to/virtual_environment/python/bin>"
Environment="ENV=PROD"
ExecStart=</absolute/path/to/virtual_environment/python/bin/>gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:5000 -m 007 src.main:app

[Install]
WantedBy=multi-user.target
```

Una vez creado, lo iniciamos: `sudo systemctl start fastapi-sia-test`. Para habilitar la posibilidad de que se inicie automáticamente junto con el sistema: `sudo systemctl enable fastapi-sia-test`. 

En este caso se asume que el archivo `.env` existe y tiene todos los valores necesarios para correr en producción y setea automáticamente la variable de entorno `ENV` como `ENV=PROD`.
