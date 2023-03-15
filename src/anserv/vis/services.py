import typing

from .vis_types import AnyVisType


def get_model_by_type(vis_type: str) -> typing.Type[AnyVisType]:
    for cls in typing.get_args(AnyVisType):
        if cls.vis_type == vis_type:
            return cls
    raise TypeError(vis_type)
