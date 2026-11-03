# API Clínica Veterinaria — Grupo 7

API REST para administrar estudiantes que atienden en una clínica veterinaria, dueños, sus mascotas y las consultas médicas. Está construida con FastAPI, SQLAlchemy, Pydantic, PostgreSQL y Alembic.

## Modelo de datos

```mermaid
erDiagram
    DUENO ||--o{ MASCOTA : tiene
    MASCOTA ||--o{ CONSULTA : recibe
    ESTUDIANTE ||--o{ CONSULTA : atiende
    DUENO {
        int id PK
        string rut UK
        string nombre_completo
        string telefono
        string direccion
    }
    MASCOTA {
        int id PK
        string nombre
        string especie
        string raza
        float peso_kg
        int dueno_id FK
    }
    ESTUDIANTE {
        int id PK
        string rut UK
        string nombre_completo
        string correo UK
        int anio_ingreso
    }
    CONSULTA {
        int id PK
        datetime fecha_hora
        string motivo
        string diagnostico
        enum estado
        int mascota_id FK
        int estudiante_id FK
    }
```

Cada mascota pertenece a un dueño. Una mascota puede tener varias consultas; cada consulta vincula una mascota con el estudiante que la atiende.

## Organización del proyecto

- `presentation/routers`: rutas HTTP, parámetros y códigos de estado.
- `presentation/schemas/dtos`: validación de entrada y salida con Pydantic.
- `application/services`: espacio para lógica de aplicación adicional.
- `domain`: espacio para reglas del dominio.
- `infrastructure/models`: entidades y relaciones SQLAlchemy.
- `infrastructure/database.py`: conexión y sesiones de base de datos.
- `infrastructure/seeders`: datos de ejemplo.
- `migrations`: cambios versionados del esquema mediante Alembic.
- `app/main.py`: crea la aplicación, registra los routers y normaliza errores.

## Reglas del negocio

1. Una consulta nueva debe programarse para una fecha y hora futuras.
2. Una consulta nueva comienza como `pendiente`. Solo puede cambiar de `pendiente` a `realizada` o `cancelada`; no se permite retroceder ni cambiar entre estados terminales.
3. Para agendar una consulta, deben existir la mascota y el estudiante relacionados, y el año de ingreso del estudiante debe estar entre 2010 y el año actual.
4. La mascota debe referenciar a un dueño existente.

## Instalación y ejecución

Requisitos: Python 3.10 o superior y Docker Desktop.

1. En la raíz del repositorio, crear y activar un entorno virtual (opcional pero recomendado):

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   ```

2. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Crear `.env` copiando `.env.example`. El valor incluido corresponde a la configuración de `docker-compose.yml`:

   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5433/veterinaria
   ```

4. Iniciar PostgreSQL y aplicar la migración:

   ```bash
   docker compose up -d
   alembic upgrade head
   ```

5. Cargar los datos de demostración (se omite la carga si alguna de las tablas ya tiene registros):

   ```bash
   python -c "from infrastructure.database import SessionLocal; from infrastructure.seeders.seeder import cargar_datos_iniciales; db = SessionLocal(); cargar_datos_iniciales(db); db.close()"
   ```

6. Iniciar la API:

   ```bash
   uvicorn app.main:app --reload
   ```

   Documentación interactiva: <http://127.0.0.1:8000/docs>. Estado del servicio: <http://127.0.0.1:8000/health>.

## Endpoints

Todos los recursos CRUD usan el prefijo `/api/v1`.

| Recurso | Rutas |
|---|---|
| Estudiantes | `GET/POST /students`, `GET/PUT/DELETE /students/{id}` |
| Dueños | `GET/POST /owners`, `GET/PUT/DELETE /owners/{id}` |
| Mascotas | `GET/POST /pets`, `GET/PUT/DELETE /pets/{id}` |
| Consultas | `GET/POST /consultations`, `GET/PATCH/DELETE /consultations/{id}` |

Las colecciones devuelven `items`, `total`, `skip` y `limit`. Las mascotas permiten filtrar por `especie` o texto (`q`), ordenar por `id`, `nombre`, `especie`, `raza` o `peso_kg`, y paginar con `limit` y `skip`. Ejemplo:

```text
GET /api/v1/pets?especie=Perro&sort_by=peso_kg&order=desc&limit=10&skip=0
```

Los errores usan la estructura `{"error":{"code":"...","message":"...","details":...}}`. Los errores de validación responden `422`, reglas de negocio `400`, referencias inexistentes `404` y conflictos de integridad `409`.

## Pruebas

Las pruebas de API usan SQLite en memoria, así que no requieren iniciar Docker:

```bash
pytest -v tests_manual
```

La suite comprueba CRUD, validación, relaciones, reglas de consultas, filtrado/orden/paginación y lectura de los datos persistidos entre solicitudes. Para comprobar persistencia tras reiniciar el proceso, iniciar la API contra PostgreSQL, crear un registro, reiniciar Uvicorn y volver a consultar el mismo ID.

## Migraciones

```bash
alembic upgrade head       # aplicar migraciones
alembic current            # revisar versión aplicada
alembic revision --autogenerate -m "descripcion"  # generar una nueva revisión
```
