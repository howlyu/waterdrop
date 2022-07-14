import codecs
import os

import yaml


class Base:

    def __init__(self):
        self.sys_config = yaml.load(codecs.open(os.path.join(
            os.path.dirname(os.path.dirname(__file__)) + "/configure.yaml"), 'r', 'utf-8'), Loader=yaml.FullLoader)

    def create(self, table_name: str):
        pass

    def start(self, job_id: int):
        pass

    def stop(self, job_id: int):
        pass

    def cancel(self, job_id: int):
        pass

    def get(self, table_name: str):
        pass

    def list(self):
        pass
