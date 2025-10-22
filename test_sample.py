"""Sample Python file for testing code quality analysis."""


def calculate_total(items):
    total = 0
    for item in items:
        if item > 0:
            total += item
        elif item < 0:
            total -= abs(item)
        else:
            pass
    return total


def complex_function(a, b, c, d, e, f):
    """A deliberately complex function for testing."""
    if a > 10:
        if b > 20:
            if c > 30:
                result = a + b + c
            else:
                result = a + b
        else:
            if d > 40:
                result = a + d
            else:
                result = a
    else:
        if e > 50:
            if f > 60:
                result = e + f
            else:
                result = e
        else:
            result = 0
    return result


class DataProcessor:
    def __init__(self, data):
        self.data = data
        self.processed = False

    def process(self):
        self.processed = True
        return [x * 2 for x in self.data]
