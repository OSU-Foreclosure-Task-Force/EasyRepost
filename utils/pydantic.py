from pydantic import BaseModel


def eliminate_missing_values(model: BaseModel) -> dict:
    return {key: value for key, value in model.model_dump() if value is not None}
