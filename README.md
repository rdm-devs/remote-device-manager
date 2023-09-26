# fastapi-sia-test

**Disclaimer**: Este es un proyecto en construcción por lo que es posible que se encuentren errores.

## ¿Cómo ejecutar el proyecto?

1. Habiendo creado un entorno virtual, procedemos con la instalación de las dependencias: `pip install -r requirements.txt`.
2. Lanzamos la aplicación FastAPI desde el directorio raíz: `uvicorn src.main:app --reload`
3. Accedemos a la documentación de la API para empezar a probar los endpoints disponibles: `http://127.0.0.1:8000/docs`.

Una base de datos de prueba (`fastapi-sia.db`) se creará automáticamente en el directorio raíz. Para ver su contenido, se puede utilizar el programa [DB Browser for SQLite](https://sqlitebrowser.org/dl/), disponible para Windows, Mac y Linux.

La estructura del proyecto está basada en estas recomendaciones: [fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices).