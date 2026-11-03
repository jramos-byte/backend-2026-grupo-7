# backend-2026-grupo-7

Reglas:

Regla 1: Una consulta no puede ser programada con una fecha y hora en el pasado.

Regla 2: El estado de una consulta solo puede avanzar (de PENDIENTE a REALIZADA o CANCELADA). Una consulta REALIZADA no puede volver a PENDIENTE.

Regla 3: Un estudiante solo puede atender una nueva consulta si su año de ingreso es valido y registrado en el sistema. 

Ejecucion del Proyecto
1. **Levantar la base de datos(Docker):**
    ```bash
    docker compose up -d

2. instalar dependencias:
    ```bash
    pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic alembic

3. Ejecutar migraciones(Alembic):
    ```bash
    alembic upgrade head

4. Ejecutar seeders:
    Para cargar los registros de prueba por entidad, ejecutar el siguiente comando en la  terminal:
    ```bash
   python -c "from infrastructure.database import SessionLocal; from infrastructure.seeders.seeder import cargar_datos_iniciales; db = SessionLocal(); cargar_datos_iniciales(db); db.close()"

5. Configurar variables de entorno:
   "Crea un archivo `.env` en la raíz del proyecto guiándote por `.env.example` y define la conexión a la base de datos:
   ```bash
   DATABASE_URL=postgresql://postgres:postgres@localhost:5433/veterinaria"