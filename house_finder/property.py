class Property:

    def __init__(self, listing):
        self.listing = listing
        self.results = []

    def __str__(self):
        return f'{self.listing}: {self.value}'

    def apply_constraints(self, constraints):
        for constraint in constraints:
            self.results.append(constraint.calculate(self.listing))

    @property
    def score(self):
        return sum(self.results)
