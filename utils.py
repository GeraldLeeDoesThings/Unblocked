from __future__ import annotations
from typing import *


T = TypeVar('T')

class Tree(Generic[T]):

    def __init__(self, head: Generic[T], children: Iterable[Tree[T]]):
        self.head = head
        self.children = [child for child in children]
