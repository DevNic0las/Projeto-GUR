from database.schemas.hospitals_schemas import HOSPITALS_SCHEMA
def create_hospitals_collection(db):
        if "hospitals" not in db.list_collection_names():
            db.create_collection(
                "hospitals",
                validator=HOSPITALS_SCHEMA,
                validationLevel="strict",
                validationAction="error"
            )
            print("✅ Coleção 'hospitals' criada com schema!")
        else:
            print("✅ Coleção 'hospitals' já existe!")
        
        return db.hospitals

    