from sqlalchemy.orm import Session
from infrastructure.models.models import Estudiante, Dueno, Mascota, Consulta, EstadoConsulta
from datetime import datetime

def cargar_datos_iniciales(db: Session):
    # Verifica si ya existen datos para evitar duplicados al reiniciar
    if db.query(Estudiante).first():
        return

    # 1.Crea Estudiantes
    est1 = Estudiante(rut="19123456-7", nombre_completo="Valentina Rojas", correo="vrojas@uct.cl", anio_ingreso=2024)
    est2 = Estudiante(rut="19765432-1", nombre_completo="Felipe Cárdenas", correo="fcardenas@uct.cl", anio_ingreso=2024)
    est3 = Estudiante(rut="20111222-3", nombre_completo="Carla Morales", correo="cmorales@uct.cl", anio_ingreso=2025)
    est4 = Estudiante(rut="20333444-5", nombre_completo="Camila Soto", correo="csoto@uct.cl", anio_ingreso=2024)
    db.add_all([est1, est2, est3, est4])
    
    # 2.Crea Dueños
    d1 = Dueno(rut="15111222-3", nombre_completo="Carlos Pinto", telefono="+56912345678", direccion="Av. Alemania 123")
    d2 = Dueno(rut="16222333-4", nombre_completo="Maria Silva", telefono="+56987654321", direccion="Caupolicán 456")
    d3 = Dueno(rut="17444555-6", nombre_completo="Pedro Sanhueza", telefono="+56911223344", direccion="San Martín 789")
    d4 = Dueno(rut="18555666-7", nombre_completo="Ana Rojas", telefono="+56944556677", direccion="Pablo Neruda 012")
    db.add_all([d1, d2, d3, d4])
    db.commit()

    # 3.Crea Mascotas vinculadas a Dueños
    m1 = Mascota(nombre="Rex", especie="Perro", raza="Pastor Alemán", peso_kg=25.5, dueño_id=d1.id)
    m2 = Mascota(nombre="Luna", especie="Gato", raza="Mestizo", peso_kg=4.2, dueño_id=d2.id)
    m3 = Mascota(nombre="Thor", especie="Perro", raza="Bulldog", peso_kg=18.0, dueño_id=d3.id)
    m4 = Mascota(nombre="Mishi", especie="Gato", raza="Siamés", peso_kg=3.5, dueño_id=d4.id)
    db.add_all([m1, m2, m3, m4])
    db.commit()

    # 4. Crear Consultas vinculando Mascota y Estudiante
    c1 = Consulta(fecha_hora=datetime(2026, 11, 2, 10, 0), motivo="Vacunación anual", estado=EstadoConsulta.PENDIENTE, mascota_id=m1.id, estudiante_id=est1.id)
    c2 = Consulta(fecha_hora=datetime(2026, 11, 3, 15, 30), motivo="Control de peso", diagnostico="Sobrepeso leve", estado=EstadoConsulta.REALIZADA, mascota_id=m2.id, estudiante_id=est2.id)
    c3 = Consulta(fecha_hora=datetime(2026, 11, 4, 11, 15), motivo="Revisión dental", estado=EstadoConsulta.PENDIENTE, mascota_id=m3.id, estudiante_id=est3.id)
    c4 = Consulta(fecha_hora=datetime(2026, 11, 5, 16, 45), motivo="Curación de herida", diagnostico="Herida limpia", estado=EstadoConsulta.REALIZADA, mascota_id=m4.id, estudiante_id=est4.id)
    db.add_all([c1, c2, c3, c4])
    db.commit()