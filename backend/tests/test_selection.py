from decimal import Decimal as D
import pytest
from app.services.selection import qualifies


@pytest.mark.parametrize('profit,sales,expected', [('101','199',True), ('99','201',True), ('101','201',True), ('99','199',False), ('100','199',True), ('99','200',True)])
def test_selection_or(profit, sales, expected):
    assert qualifies(D(profit), D(sales), D('100'), D('200')) is expected


def test_selection_missing_or_non_finite_does_not_pass():
    for value in (None, D('NaN'), D('Infinity')):
        with pytest.raises(ValueError):
            qualifies(value, D('201'), D('100'), D('200'))
