from enum import Enum
from typing import Any, Callable, Union
from ipywidgets import FloatSlider, IntSlider, IntRangeSlider, Text, interactive, Layout, HTML, HBox, VBox
from inspect import getargspec
from typing import Callable
from IPython.display import display
import yaml

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

class TextParameter(InteractiveParameter):
    T = str
    def __init__(self, name: str, value: T, description: str = "", group="default"):
        self.validate_argument(value)
        super().__init__(Text, name, value, None, None, None, description, group)

class ParameterType(Enum):
    floats = FloatParameter
    ints = IntParameter
    intranges = IntRangeParameter
    texts = TextParameter

class InteractiveUtils:
    def __init__(self):
        raise Exception("This class should not be instantiated.")
    
    @classmethod
    def plotInteractive(cls, callback: Callable, params: list[InteractiveParameter]):
        sliders_groups = {item.name: item.group for item in params}
        sliders_list = {item.name: item.slider() for item in params}

        args = getargspec(callback).args
        widgets = interactive(callback, **sliders_list)
        controls = widgets.children[:-1]
        graph = widgets.children[-1]
        
        grouped_widgets = {group: [] for group in set([item.group for item in params])}
        for name, widget in zip(args, controls):
            grouped_widgets[sliders_groups[name]].append(widget)

        widget_title_group = [
            VBox([
                HTML(value=f"<b>{name}</b>"), 
                HBox(widget_group, layout = Layout(flex_flow='row wrap')), 
                HTML(value="<br>")
            ])
            for name, widget_group in grouped_widgets.items()
        ]

        ordered_group = [x for _, x in sorted(zip(grouped_widgets.keys(), widget_title_group))]

        display(VBox(ordered_group))
        display(graph)

    @classmethod
    def loadSimulationConfigFile(cls, path: str) -> list[InteractiveParameter]:
        with open(path, 'r') as file:
            groups_config, params_config = list(yaml.safe_load_all(file))

        groups = {item['name']:item['description'] for item in groups_config}
        types = list(filter(lambda x: not x.startswith("_"), dir(ParameterType)))
        params = []

        for t in types:
            if t not in params_config:
                continue
            params += [getattr(ParameterType, t).value(**item) for item in params_config[t]]

        for param in params:
            param.group = groups[param.group]

        return params