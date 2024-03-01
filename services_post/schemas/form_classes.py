from dataclasses import dataclass, asdict
from typing import Optional

from fastapi import Form
from pydantic import UUID4
from schemas import CreatePost, UpgradePost




class ToDict:
    def to_dict(self):
        dict_: dict =  asdict(self)
        return dict(filter(lambda item: bool(item[1]), dict_.items()))




@dataclass
class CreatePostClass(ToDict):
    title: str = Form(...)
    content: str = Form(...)
    
    def __post_init__(self
            ):
        model = CreatePost
        checker_model = check_model(
            model=model,
            title=self.title,
            content=self.content,
        )

        return checker_model


@dataclass
class UpgradePostClass(ToDict):
    title: Optional[str] = Form(default=None)
    content: Optional[str] = Form(default=None)
    
    def __post_init__(self
            ):
        model = UpgradePost
        checker_model = check_model(
            model=model,
            title=self.title,
            content=self.content,
        )
        return checker_model
        
    
def check_model(model, **data):
        checker_model = model(**data).model_dump_json(exclude_unset=True, exclude_none=True, exclude_defaults=True)
        return checker_model