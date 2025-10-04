from dataclasses import dataclass, fields


class BaseDataClass:
    def validate(self):
        for field in fields(self):
            if (
                field.default is not None
                or field.default_factory != dataclass._MISSING_TYPE
            ):
                continue

            value = getattr(self, field.name)
            if value is None:
                raise ValueError(f"Missing required field: {field.name}")
