HOSPITALS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "location", "illness"],
        "properties": {
            "name": {
                "bsonType": "string",  
                "minLength": 5,
                "maxLength": 100,      
                "description": "Nome do hospital - obrigatório"  #
            },
            "location": {
                "bsonType": "string",  # ✅ "string" minúsculo
                "description": "Localização - obrigatório"  # ✅ ortografia
            },
            "illness": {
                "bsonType": "array",
                "description": "Lista de doenças tratadas pelo hospital",
                 "items": {
                     "bsonType": "string"
                 }
            }
            
        }
    }
}