class Base:

    def __init__(self):
        self.data = []

    def create(self, table_name: str):
        pass

    def start(self, job_id: int):
        pass

    def stop(self, job_id: int):
        pass

    def cancel(self, job_id: int):
        pass

    def get(self, job_id: int):
        pass

    def list(self):
        pass
