from dataclasses import dataclass
from typing import List

@dataclass
class Page:
    url:str
    h1:List[str]
    h2:List[str]
    h3:List[str]
    h4:List[str]
    h5:List[str]
    text:str

    def get_text_summary(self):
        return self.text[:100]