from .base import BasePipeline
from ..utils import get_search_map


class Pipeline(BasePipeline):

    def __init__(self, steps_as_str):
        assert isinstance(steps_as_str, (list, str))
        search_map = get_search_map()
        if isinstance(steps_as_str, str) and not steps_as_str == 'all':
            raise ValueError('steps_as_str deve ser uma lista ou `all`')
        if steps_as_str == 'all' or any(map(lambda x: x == 'all', steps_as_str)):
            steps = list(search_map.values())
        else:
            steps = [search_map[step] for step in steps_as_str if search_map.get(step, False)]

        l_steps = []
        for step in steps:
            if isinstance(step, list):
                for sub_step in step:
                    l_steps.append(sub_step)
            else:
                l_steps.append(step)
        super().__init__(l_steps)
