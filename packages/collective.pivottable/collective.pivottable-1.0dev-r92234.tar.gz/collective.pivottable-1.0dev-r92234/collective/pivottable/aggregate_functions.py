

class BaseAggregate(object):
    def __init__(self, init_value=None):
        self.values = []
        self.init_value = init_value

    def append(self, value):
        self.values.append(value)

class GroupBy(object):
    def __init__(self):
        self.values = set()

    def append(self, value):
        self.values.add(value)

class Sum(BaseAggregate):
    def __call__(self):
        return sum(self.values)

class Avg(BaseAggregate):
    def __call__(self):
        if not len(self.values):
            return None

        if self.init_value:
            return sum(self.values + [self.init_value]) / float(len(self.values))
        return sum(self.values) / float(len(self.values))

class Min(BaseAggregate):
    def __call__(self):
        return min(self.values)

class Max(BaseAggregate):
    def __call__(self):
        return max(self.values)

class First(BaseAggregate):
    def __call__(self):
        if len(self.values):
            return self.values[0]

class Last(BaseAggregate):
    def __call__(self):
        if len(self.values):
            return self.values[-1]
