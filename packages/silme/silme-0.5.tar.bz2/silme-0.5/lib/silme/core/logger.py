import silme.core
"""
Basic logger class.
It adds to EntityList, L10nObject and L10nPackage methods:
class.log(type, message, path=None)
class.get_logs()

that allows to store informations about the package or object.
"""

class Logger():
    @classmethod
    def log(cls, type, message, path=None):
        """
        adds a new log to the object.
        """
        if hasattr(cls, 'logs'):
            cls.logs.append((type, message, path))
        else:
            cls.logs = [(type, message, path)]
        return True

    @classmethod
    def get_logs(cls):
        """
        returns list of logs for Logger
        """
        if hasattr(cls, 'logs'):
            return cls.logs
        return []

def log(self, type, message, path=None):
    """
    adds a new log to the object. If self.logs list does not exist its being added
    """
    if hasattr(self, 'logs'):
        self.logs.append((type, message, path))
    else:
        self.logs = [(type, message, path)]
    return True

def get_logs(self):
    """
    returns list of logs for the object
    """
    if hasattr(self, 'logs'):
        return self.logs
    return []

def get_all_logs(self, recursive=False):
    """
    returns list of logs for the package, optionally can also load
    all logs from its objects and sub-packages.
    """
    if hasattr(self, 'logs'):
        logs = self.logs
    else:
        logs = []
    if not recursive:
        return logs
    for object in self.get_objects():
        logs.extend(object.get_logs())
    for package in self.get_packages():
        logs.extend(package.get_logs(recursive=True))
    return logs


silme.core.EntityList.log = log
silme.core.EntityList.get_logs = get_logs

silme.core.L10nObject.log = log
silme.core.L10nObject.get_logs = get_logs

silme.core.L10nPackage.log = log
silme.core.L10nPackage.get_logs = get_all_logs
