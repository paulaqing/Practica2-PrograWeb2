from datetime import datetime
from bson import ObjectId

def serialize_doc(doc):
    """
    Convierte documentos de MongoDB (BSON) a diccionarios estándar JSON compatibles,
    transformando ObjectIds en strings (tanto 'id' como '_id') y serializando fechas.
    """
    if doc is None:
        return None
        
    # Si es una lista, serializar recursivamente cada elemento
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
        
    if not isinstance(doc, dict):
        if isinstance(doc, ObjectId):
            return str(doc)
        if isinstance(doc, datetime):
            return doc.isoformat()
        return doc
        
    new_doc = {}
    for k, v in doc.items():
        if k == "_id":
            val_str = str(v)
            new_doc["id"] = val_str
            new_doc["_id"] = val_str
        elif isinstance(v, ObjectId):
            new_doc[k] = str(v)
        elif isinstance(v, datetime):
            new_doc[k] = v.isoformat()
        elif isinstance(v, dict):
            new_doc[k] = serialize_doc(v)
        elif isinstance(v, list):
            new_doc[k] = [serialize_doc(item) for item in v]
        else:
            new_doc[k] = v
            
    return new_doc
