#-*- coding: utf-8 -*-

from models import GameModel


class UserTask(GameModel):
    """ 玩家任务数据
    """ 
    def __init__(self, uid=''):
        # 玩家任务数据
        self.uid = uid 
        self.has_new_task = False # 有新任务或有已完成任务
        self.main_task = {} 

    @classmethod
    def create(cls, uid): 
        obj = super(UserTask, cls).create(uid)
        obj.init()
        return obj

    def init(self):
        main_task_conf = self._task_config['main_task']
        user_lv = self.user_property.lv
        for task_id, info in main_task_conf.items():
            if 'open_lv' in info and info['open_lv'] <= user_lv:
                self.add_main_task(task_id)
        self.has_new_task = True

    def add_main_task(self, task_id):
        if task not in self.main_task:
            self.main_task[task_id] = {
                'step': '1',
                'completed': False,
                'now_value': None,
            }
            self.turn_new_task(True)

    def del_main_task(self, task_id):
        self.main_task.pop(task_id)

    def has_task(self, task_id):
        return task_id in self.main_task

    def set_now_value(self, task_id, value):
        self.main_task[task_id]['now_value'] = value

    def get_now_value(self, task_id):
        if self.main_task[task_id]['now_value'] is None:
            return 0
        return self.main_task[task_id]['now_value']

    def set_step(self, task_id, step):
        self.main_task[task_id]['step'] = step

    def set_completed(self, task_id, completed=True):
        self.main_task[task_id]['completed'] = completed
        if completed:
            self.turn_new_task(True)

    def turn_new_task(self, flag):
        if flag is False:
            # 有已完成，还是要标记
            for task_info in self.main_task.values():
                if task_info['completed']:
                    self.has_new_task = True
                    return
        self.has_new_task = flag
         
