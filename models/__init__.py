#!/usr/bin/env python
# encoding: utf-8

import json
import ast
from libs.model import UserModel
from common.game_config import get_config_dir


class GameModel(UserModel):
    """
    对UserModel 进一步封装一些通用 方法，便于应用的 user_model， 例如：
    game_model_obj.other_game_model_name        获得此id的其他game_model
    game_model_obj._config_name 获得游戏配置

    """

    _ALL_USER_CLASSES = {}

    @classmethod
    def create(cls, uid):
        return cls(uid) 

    @classmethod
    def get_no_none(cls, uid):
        return cls.get(uid) or cls.create(uid)
    
    def get_config(self, config_name):
        return get_config_dir(config_name)

    def __getattr__(self, model_name):
        if model_name.startswith('_') and model_name.endswith('_config'):
            return self.get_config(model_name[1:])
        class_name = "".join([name_str.capitalize() for name_str in model_name.split('_')]) 
        if class_name == self.__class__.__name__:
            return self
        if model_name in self._ALL_USER_CLASSES:
            return self._ALL_USER_CLASSES[model_name].get_no_none(self.uid) 
        model_path = "models." + model_name
        try:
            model = __import__(model_path, globals(), locals(), [class_name])
            model_class = getattr(model, class_name)
        except ImportError:
            raise AttributeError, "{} object has no attribute '{}'".format(self.__class__.__name__, model_name)
        # 只有继承自GameModel的类实例，才能相互调取
        if self.__class__.__bases__ != model_class.__bases__:
            raise AttributeError, "{} object is not a GameModel".format(model_name)
        self._ALL_USER_CLASSES[model_name] = model_class
        return model_class.get_no_none(self.uid) 

