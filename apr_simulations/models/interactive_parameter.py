from typing import Any, Callable, Union
from ipywidgets import FloatSlider, IntSlider, IntRangeSlider

class InteractiveParameter:
    T = Any
    def __init__(self, callback: Callable, name: str, value: Any, min: Union[int, float], max: Union[int, float], step: Union[int, float], description: str = "", group="default"):
        self.callback = callback
        self.name = name
        self.value = value
        self.min = min
        self.max = max
        self.step = step
        self.description = description
        self.group = group
        self._expand_description = False

    @property
    def slider_style(self):
        return {'description_width': 'initial', 'value_width': 'initial'}

    def slider(self):
        description = f"{self.description}" 
        if self.expand_description:
            description += f"({self.name})"

        return self.callback(min=self.min, max=self.max, step=self.step, value=self.value, description=description, style=self.slider_style)
    
    def validate_argument(self, item: Any):
        if not isinstance(item, self.T):
            raise TypeError(f"One argument doesn't match expected type. Should be {self.T}.")
    
    @property
    def expand_description(self):
        return self._expand_description
    
    @expand_description.setter
    def expand_description(self, value):
        self._expand_description = value

class FloatParameter(InteractiveParameter):
    T = float
    def __init__(self, name: str, value: T, min: T, max: T, step: T, description: str = "", group="default"):
        [self.validate_argument(item) for item in [value, min, max, step]]
        super().__init__(FloatSlider, name, value, min, max, step, description, group)

class IntParameter(InteractiveParameter):
    T = int
    def __init__(self, name: str, value: T, min: T, max: T, step: T, description: str = "", group="default"):
        [self.validate_argument(item) for item in [value, min, max, step]]
        super().__init__(IntSlider, name, value, min, max, step, description, group)

class IntRangeParameter(InteractiveParameter):
    T = int
    def __init__(self, name: str, value: list[T], min: T, max: T, step: T, description: str = "", group="default"):
        [self.validate_argument(item) for item in [*value, min, max, step]]
        super().__init__(IntRangeSlider, name, value, min, max, step, description, group)
