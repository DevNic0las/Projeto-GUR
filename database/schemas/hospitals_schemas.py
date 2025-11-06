HOSPITALS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "location"],
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
            }
            
        }
    }
}