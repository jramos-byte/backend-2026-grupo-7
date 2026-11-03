from fastapi import FastAPI
from presentation.routers import duenos, mascotas, consultas

app = FastAPI(title="Sistema Veterinario - Backend")

# Registrar los tres routers
app.include_router(duenos.router)
app.include_router(mascotas.router)
app.include_router(consultas.router)