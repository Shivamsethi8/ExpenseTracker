import os
from datetime import datetime, timedelta
import random
import bson

DEBUG = False

CURRENT_MONTH = datetime.now().strftime("%B-%Y")

CATEGORIES = [
    "water",
    "electricity",
    "rent",
    "automobile-loan",
    "home-loan",
    "groceries",
    "internet",
    "phone",
    "entertainment",
    "travel",
    "fuel",
    "eat-outs"
]

DEFAULT_VALUE = 0.0

DEFAULT_CONFIG = {
    "categories": CATEGORIES,
    "data": {
       CURRENT_MONTH: {
            "expenses": {category: DEFAULT_VALUE for category in CATEGORIES},
            "income": DEFAULT_VALUE,
            "savings": DEFAULT_VALUE,
        }
    }
}


class ConfigurationError(Exception):
    pass


class Configuration(object):
    def __init__(self):
        super(Configuration, self).__init__()
        self.__configdir__ = os.path.join(
            os.environ.get("HOME"), ".config", "expense_tracker"
        )
        self.__configfile__ = os.path.join(self.__configdir__, "expense_tracker.conf")
        self.__config__ = None
        self._ensure()
        self._read()

        if not self.__config__:
            if DEBUG:
                self.initialise_test_config()
            else:
                self.initialise_config()

        self.ensure_current_month_data()

    def _ensure(self):
        if not os.path.isdir(self.__configdir__):
            os.makedirs(self.__configdir__, mode=0o755)
        if not os.path.isfile(self.__configfile__):
            with open(self.__configfile__, "wb") as config:
                config.write(bson.dumps({}))

    def _read(self):
        with open(self.__configfile__, "rb") as config:
            self.__config__ = bson.loads(config.read())

    def _write(self):
        with open(self.__configfile__, "wb") as config:
            config.write(bson.dumps(self.__config__))

    def get(self):
        return self.__config__

    def set(self, config_dict):
        self.__config__ = config_dict
        self._write()

    def reset(self,):
        self.__config__ = {}
        self._write()

    def add_section(self, section):
        if section in self.__config__:
            raise ConfigurationError("Section \"{}\" already exists.".format(section))

        self.__config__.setdefault(section, {})
        self._write()

    def get_section(self, section):
        if section not in self.__config__:
            raise ConfigurationError("Section \"{}\" does not exist.".format(section))

        return self.__config__[section]

    def set_section(self, section, config):
        if section not in self.__config__:
            raise ConfigurationError("Invalid section: \"{}\"".format(section))
        self.__config__[section] = config
        self._write()

    def update_section(self, section, changes):
        if section not in self.__config__:
            raise ConfigurationError("Invalid section: \"{}\"".format(section))
        self.__config__[section].update(changes)
        self._write()

    def has_section(self, section):
        return section in self.__config__

    def reset_section(self, section):
        if section not in self.__config__:
            raise ConfigurationError("Invalid section: \"{}\"".format(section))
        self.__config__[section] = {}
        self._write()

    def delete_section(self, section):
        if section not in self.__config__:
            raise ConfigurationError("Invalid section: \"{}\"".format(section))
        del self.__config__[section]
        self._write()

    def get_history_months(self):
        last_date = datetime.strptime(CURRENT_MONTH, get_date_format())

        month_keys = [CURRENT_MONTH]

        for interval in range(1, 6):
            last_date = last_date - timedelta(weeks=4)
            month_keys.append(last_date.strftime(get_date_format()))

        return month_keys

    def initialise_config(self):
        self.set(DEFAULT_CONFIG)

        for key in self.get_history_months():
            default_config = {key: DEFAULT_CONFIG["data"][CURRENT_MONTH]}
            default_config[key]["expenses"] = {
                category: DEFAULT_VALUE for category in self.get_section("categories")
            }
            self.update_section("data", default_config)

    def initialise_test_config(self):
        self.set(DEFAULT_CONFIG)

        monthly_config = {
            current_month: {
                "expenses": {category: random.randint(100, 10000) for category in CATEGORIES},
                "income": random.randint(150000, 200000),
                "savings": random.randint(25000, 40000)
            }
            for current_month in self.get_history_months()
        }
        self.update_section("data", monthly_config)

    def ensure_current_month_data(self):
        if not self.get_section("data").get(CURRENT_MONTH):
            self.update_section("data", DEFAULT_CONFIG["data"])


def get_date_format():
    return "%B-%Y"
