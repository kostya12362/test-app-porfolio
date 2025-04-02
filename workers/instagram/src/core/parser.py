from pydantic import BaseModel


class BaseParser:
    instance: type[BaseModel]

    @property
    def get_data(self) -> BaseModel:
        if not hasattr(self, 'instance'):
            raise AttributeError('instance attribute not found')
        fields = list(self.instance.__annotations__.keys())
        data = dict()
        for field in fields:
            data[field] = getattr(self, field)
        return self.instance(**data)
