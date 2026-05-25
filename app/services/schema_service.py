class SchemaService:

    @staticmethod
    def validate_data(schema: dict, data: dict):

        for field in schema.keys():
            if field not in data:
                return False, f"Missing field: {field}"

        return True, "Valid"