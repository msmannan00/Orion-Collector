from abc import abstractmethod, ABC
from typing import Tuple, Set
from dynamic_collector.lib.model.collector_data_model import collector_data_model


class collector_interface(ABC):
    @abstractmethod
    def parse_leak_data(self, html_content: str, p_data_url:str) -> Tuple[collector_data_model, Set[str]]:
        """Parse leak data from HTML content and return a tuple of leak_data_model and a set of sub-links."""
        pass
