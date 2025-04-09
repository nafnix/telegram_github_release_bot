from enum import StrEnum, auto

from .alias_generators import to_camel, to_pascal, to_snake


__all__ = [
    "CamelEnum",
    "NameEnum",
    "PascalEnum",
    "SnakeEnum",
    "TitleEnum",
    "auto",
]


class NameEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name, *_, **__) -> str:
        return name


class PascalEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name, *_, **__) -> str:
        return to_pascal(name)


class CamelEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name, *_, **__) -> str:
        return to_camel(name)


class SnakeEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name, *_, **__) -> str:
        return to_snake(name)


class TitleEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name, *_, **__) -> str:
        return name.replace("_", " ").title()
