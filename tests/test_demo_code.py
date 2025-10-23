import pytest
from demo_code import calculate_discount, process_order

# Tests for calculate_discount

def test_calculate_discount_normal():
    assert calculate_discount(100, 10) == 90


def test_calculate_discount_over_100():
    # Discount capped at 100%
    assert calculate_discount(200, 150) == 0


def test_calculate_discount_negative():
    # Negative discount treated as 0%
    assert calculate_discount(50, -5) == 50


def test_calculate_discount_zero_discount():
    assert calculate_discount(80, 0) == 80

# Tests for process_order

def test_process_order_simple():
    items = [
        {'price': 10, 'quantity': 2},
        {'price': 5,  'quantity': 1},
    ]
    assert process_order(items) == 25


def test_process_order_zero_quantity():
    items = [
        {'price': 10, 'quantity': 0},
        {'price': 5,  'quantity': 3},
    ]
    assert process_order(items) == 15


def test_process_order_negative_quantity():
    items = [
        {'price': 10, 'quantity': -2},
        {'price': 5,  'quantity': 3},
    ]
    # Negative quantity should be ignored
    assert process_order(items) == 15


def test_process_order_multiple_items():
    items = [
        {'price': 2, 'quantity': 5},
        {'price': 3, 'quantity': 4},
        {'price': 1, 'quantity': 10},
    ]
    assert process_order(items) == (2*5 + 3*4 + 1*10)

# Edge case: empty list

def test_process_order_empty():
    assert process_order([]) == 0
