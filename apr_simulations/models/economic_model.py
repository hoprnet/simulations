class Equation:
    def __init__(self, formula: str, condition: str):
        self.formula = formula
        self.condition = condition


class Equations:
    def __init__(self, f_x: Equation, g_x: Equation):
        self.f_x = f_x
        self.g_x = g_x


class Parameters:
    def __init__(self, a: float, b: float, c: float, l: float):  # noqa: E741
        self.a = a
        self.b = b
        self.c = c
        self.l = l


class BudgetParameters:
    def __init__(
        self,
        budget: float,
        period: float,
        s: float,
        distribution_frequency: float,
        ticket_price: float,
        winning_probability: float,
    ):
        self.budget = budget
        self.period = period
        self.s = s
        self.distribution_frequency = distribution_frequency
        self.ticket_price = ticket_price
        self.winning_probability = winning_probability

    @property
    def delay_between_distributions(self):
        return self.period / self.distribution_frequency


class EconomicModel:
    def __init__(
        self, equations: Equations, parameters: Parameters, budget: BudgetParameters
    ):
        self.equations = equations
        self.parameters = parameters
        self.budget = budget

    def transformed_stake(self, stake: float):
        # convert parameters attribute to dictionary
        kwargs = vars(self.parameters)
        kwargs.update({"x": stake})

        if eval(self.equations.f_x.condition, kwargs):
            func = self.equations.f_x
        else:
            func = self.equations.g_x

        return eval(func.formula, kwargs)

    @property
    def delay_between_distributions(self):
        return self.budget.delay_between_distributions
