
class EstudiantesRouter:
    """
    Dirige las consultas de EstudianteEstatico a la base estática.
    Impide modificar esa tabla desde la aplicación.
    """

    def db_for_read(self, model, **hints):
        if model._meta.model_name == 'estudianteestatico':
            return 'estudiantes_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.model_name == 'estudianteestatico':
            return 'estudiantes_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.model_name == 'estudianteestatico'
            or obj2._meta.model_name == 'estudianteestatico'
        ):
            return obj1._state.db == obj2._state.db
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == 'estudianteestatico':
            return False
        return db == 'default'
