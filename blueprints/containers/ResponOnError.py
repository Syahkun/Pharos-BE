
from blueprints.containers.base import ContainerBase

class ResponOnError(ContainerBase):
    def __init__(self):
       self.message = "Failed"
       self.error_key = None
       self.error_message = None
       self.error_data = {}