# 🏥 API Clínica Veterinaria Universitaria — Grupo 7

API REST desarrollada con **FastAPI** para la gestión asistencial de estudiantes de veterinaria, dueños, mascotas y consultas dentro de la clínica práctica universitaria.

---

## 🏗️ Arquitectura y Capas del Proyecto

El proyecto sigue los principios de Arquitectura Limpia (*Clean Architecture*) dividida en las siguientes capas:

- **`app/`**: Punto de entrada de la aplicación (`main.py`).
- **`presentation/`**: Capa de presentación y contratos HTTP.
  - `routers/`: Endpoints de la API (`/students`, `/owners`, `/pets`, `/consultations`).
  - `schemas / dtos/`: Validaciones de datos de entrada/salida mediante Pydantic.
  - `dependencies.py`: Inyección de dependencias (ej. sesiones de base de datos).
- **`application/`**: Casos de uso y servicios que contienen la lógica de negocio (`services/`).
- **`domain/`**: Entidades centrales y reglas del dominio del sistema.
- **`infrastructure/`**: Detalles técnicos de persistencia y conexión.
  - `models/`: Modelos ORM (SQLAlchemy).
  - `repositories/`: Acceso directo a la base de datos.
  - `mappers/`: Mapeo entre modelos ORM y entidades del dominio.
  - `seeders/`: Scripts de carga inicial de datos de prueba (`seeder.py`).
- **`migrations/`**: Historial y versiones de migraciones gestionadas por Alembic (`alembic.ini`).
- **`tests_manual/`**: Scripts de pruebas de verificación de endpoints y persistencia.

---

## 🚀 Requisitos Previos

- **Python 3.10+**
- **Docker Desktop** (con soporte para PostgreSQL)

---

## 🛠️ Instalación y Configuración Local

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd backend-2026-grupo-7