import os
import logging
from typing import List
from abc import abstractmethod

logger = logging.getLogger(__name__)


class CreateFolderException(Exception):
    def __init__(self, message):
        super(CreateFolderException, self).__init__(message)


class Field:

    def __init__(self, name: str, default_value: any = None) -> None:
        self.name = name
        self.default_value = default_value


class Folder:

    def __init__(self, path: str) -> None:
        self.path = path
        self.sub_folders = []

    def add_sub_folder(self, folder):
        folder.path = os.path.join(self.path, folder.path)
        self.sub_folders.append(folder)

    def create_folder(self) -> None:
        try:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
        except OSError:
            message = 'Not was possible create the folder on the directory {}'.format(
                self.path)
            logger.error(message, exc_info=True)
            raise CreateFolderException(message)

        self._create_sub_folders()

    def _create_sub_folders(self) -> None:
        for folder in self.sub_folders:
            folder.create_folder()

    def __repr__(self) -> str:
        return '{}({})'.format(__class__, self.path)

    def __str__(self) -> str:
        return self.path


class Template:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    BASE_TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')

    def __init__(self, file_path: str, fields: List[Field] = None) -> None:
        self.file_path = os.path.join(self.BASE_TEMPLATE_FOLDER, file_path)
        self.fields = fields
        self._content = None

    @abstractmethod
    def load(self):
        raise NotImplementedError('The load method should be implement')


class LocalTemplate(Template):

    def __init__(self, file_path: str, fields: List[Field] = None) -> None:
        super().__init__(file_path, fields)

    def load(self):
        try:
            with open(self.file_path, 'r') as file:
                self._content = file.read()
            return self._content
        except UnicodeDecodeError:
            message = 'Template file {} should be a valid utf-8 file'.format(
                self.file_path)
            logger.error(message, exc_info=True)
            raise ValueError(message)


class Project:

    def __init__(self, name: str, root_folder: Folder, folders: List[Folder]) -> None:
        self.name = name
        self.root_folder = root_folder
        self.folders = folders

    def create_folders(self):
        for folder in self.folders:
            self.root_folder.add_sub_folder(folder)
        self.root_folder.create_folder()

        logger.info('{} project folders created'.format(self.name))

    def __repr__(self) -> str:
        return '{}({}, {})'.format(__class__, self.name, self.root_folder, self.folders)

    def __str__(self) -> str:
        return self.name
