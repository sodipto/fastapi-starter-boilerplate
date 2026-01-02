from sqlalchemy.schema import CreateSchema

class DbSchemas:
    identity = "Identity"
    logger = "Logger"

def ensure_schemas_exist(engine):
    for schema_name in (value for key, value in vars(DbSchemas).items() if not key.startswith("__") and isinstance(value, str)):
        engine.execute(CreateSchema(schema_name, if_not_exists=True))