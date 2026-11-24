"""Replaceable integration boundaries only; no external capabilities are claimed."""
from typing import Protocol, Any


class PublicDataAdapter(Protocol):
    def fetch(self, query: dict[str, Any]) -> dict[str, Any]: ...


class InfringementAdapter(Protocol):
    def check(self, product: dict[str, Any]) -> dict[str, Any]: ...


class ModelAdapter(Protocol):
    def generate(self, request: dict[str, Any]) -> dict[str, Any]: ...


class ListingAdapter(Protocol):
    def submit(self, request: dict[str, Any]) -> dict[str, Any]: ...
