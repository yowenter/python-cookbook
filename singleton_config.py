import logging

LOG = logging.getLogger(__name__)


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if class_._instance is None:
            class_._instance = object.__new__(class_, *args, **kwargs)
            LOG.info("class `%s`, inited `%s`", class_, class_._instance)
        return class_._instance


class Parameter(object):
    def __init__(self, name, value, value_type=None, default=None, comment=None):
        self.name = name
        self.value = self.validate_value(value, value_type, default)
        self.comment = comment

    def validate_value(self, value, value_type, default):
        if value is None:
            if callable(default):
                value = default()
            else:
                value = default

        if value is None:
            LOG.warn("Param `%s` is None", self.name)

        if value_type is not None:
            self.check_value(value, value_type)

        return value

    def check_value(self, value, value_type):
        pass

    def as_dict(self):
        return dict(
            name=self.name,
            value=self.value,
            comment=self.comment
        )

    @classmethod
    def from_dict(cls, data):
        name = data.get('name')
        value = data.get('value')
        comment = data.get('comment')
        value_type = data.get('value_type')
        default = data.get('default')

        assert (name is not None), 'Parameter field name missed'
        return cls(name, value, value_type=value_type, comment=comment, default=default)


class Section(object):
    def __init__(self, name, params=None):
        self.name = name
        self.params_dict = dict()
        for param in params:
            if param.name in self.params_dict:
                LOG.warn("Parameter name `%s` conflict", param.name)
            else:
                self.params_dict[param.name] = param.as_dict()

    def __getattr__(self, name):
        if name in self.params_dict:
            return self.params_dict[name]['value']
        else:
            return None


class Config(Singleton):
    def __init__(self, sections):
        self.sections = sections
        self.section_dict = {s.name: s for s in sections}

    def __getattr__(self, name):
        if name in self.section_dict:
            return self.section_dict[name]

        else:
            for s in self.sections:
                if getattr(s, name) is not None:
                    return getattr(s, name)

    @classmethod
    def from_dict(cls, config_data):
        '''
        @config_data : { 'database_settings':[{'name':'MYSQL_DB_HOST':'value':"mysql://localhost:3306/test"}]}

        '''
        sections = list()
        for name, params_data in config_data.items():
            params = [Parameter.from_dict(p) for p in params_data]
            section = Section(name, params)
            sections.append(section)

        return cls(sections)


if __name__ == '__main__':
    config = Config.from_dict(

        {'database':
            [

                {
                    'name': 'MYSQL_DATABASE_HOST',
                    'value': 'mysql://localhost:3306/test'
                }

            ]
        }

    )

    print config.database

    print config.MYSQL_DATABASE_HOST
    s = Section(
        'mysql', [Parameter.from_dict({'name': 'database_url', 'value': 'test'})])
    print s.database_url

    config1 = Config([s])
    config2 = Config([])

    print id(config1), id(config2)
