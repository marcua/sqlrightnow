from dataclasses import dataclass

from sqlrightnow.storage import AbstractStorage
from sqlrightnow.engine import AbstractEngine


@dataclass
class DBManager:
    storage: AbstractStorage
    engine: AbstractEngine
    cleanup_working_path: bool = False

    def local_path(self):
        if not self.__working_path:
            # Stopped working here. Notes:
            # - Make a dirctory with mkdtemp
            # - Clean up with something like https://stackoverflow.com/questions/6884991/how-to-delete-a-directory-created-with-tempfile-mkdtemp  # noqa
            self.__local_path = self.storage.retrieve()
