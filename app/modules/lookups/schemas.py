from pydantic import BaseModel

class LookupOut(BaseModel):
    id: int
    category: str
    value: str

    model_config = {"from_attributes": True}

class AllLookupsOut(BaseModel):
    gas_types: list[str]
    capacity_units: list[str]
    tank_statuses: list[str]
    measurement_methods: list[str]
    plants: list[str]
