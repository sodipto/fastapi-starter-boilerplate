from sqlalchemy.schema import CreateSchema

class DbSchemas:
    identity = "Identity"
    logger = "Logger"

def ensure_schemas_exist(engine):
    for schema_name in vars(DbSchemas).values():
        if isinstance(schema_name, str):
            engine.execute(CreateSchema(schema_name, if_not_exists=True))