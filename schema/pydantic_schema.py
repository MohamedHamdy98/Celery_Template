from pydantic import BaseModel
from typing import List

# Template schema for download video based on URL.
class URLs(BaseModel):
    urls: List[str]
    
