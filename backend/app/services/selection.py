"""Confirmed OR rule only; calculation inputs and policy are not yet configured.

This standalone domain function is not wired to collection or pool admission.
"""
from decimal import Decimal


def qualifies(profit: Decimal | None, monthly_sales: Decimal | None, profit_threshold: Decimal | None, monthly_threshold: Decimal | None) -> bool:
    values = (profit, monthly_sales, profit_threshold, monthly_threshold)
    if any(value is None or not isinstance(value, Decimal) or not value.is_finite() for value in values):
        raise ValueError('完整、有限的测算结果及阈值必填；缺失不能自动通过')
    # Inclusive boundary is a conservative design assumption pending confirmation.
    return profit >= profit_threshold or monthly_sales >= monthly_threshold
