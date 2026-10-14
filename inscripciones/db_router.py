# inscripciones/db_router.py

class EstudiantesRouter:
    """
    Enrutador para direccionar las consultas de EstudianteEstatico
    a la base de datos estática.
    """
    route_app_labels = {'inscripciones'}

    def db_for_read(self, model, **hints):
        if model._meta.model_name == 'estudianteestatico':
            return 'estudiantes_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.model_name == 'estudianteestatico':
            return 'estudiantes_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == 'estudianteestatico':
            return db == 'estudiantes_db'
        return db == 'default'