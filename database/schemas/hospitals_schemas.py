HOSPITALS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "location", "illness", "specialty", "type"],
        "properties": {
            "name": {
                "bsonType": "string",  
                "minLength": 5,
                "maxLength": 100,      
                "description": "Nome do hospital - obrigatório"  
            },
            "location": {
                "bsonType": "string",  
                "description": "Localização - obrigatório"  
            },
            "illness": {
                "bsonType": "array",
                "description": "Lista de doenças tratadas pelo hospital",
                 "items": {
                     "bsonType": "string"
                 }
            },
            "type": {
                "bsonType": "string",
                "description": "Tipo de emergência"
            },
            "specialty":{
                "bsonType": "array",
                "description": "Especialidade do hospital",
                "items": {
                    "bsonType": "string"
                }
            }
            
        }
    }
}


