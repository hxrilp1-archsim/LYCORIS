class ImportError(Exception):
    """Error base de importación"""
    pass


class ZipError(ImportError):
    """Error al procesar archivos ZIP"""
    pass


class StructureError(ImportError):
    """Error en la estructura de la novela"""
    pass


class ValidationError(ImportError):
    """Error de validación"""
    pass
