import requests

try:
    import simplejson as json
except ImportError:
    import json

import diamond.collector


class HTTPRabbitMQCollector(diamond.collector.Collector):
    """A simple rabbitmq collector that uses the HTTP mgmt API."""

    STATS = ['memory', 'messages_ready', 'messages_unacknowledged',
             'messages', 'consumers']

    HTTP_HEADERS = {"content-type": "application/json"}

    def get_default_config_help(self):
        config_help = super(HTTPRabbitMQCollector, self).get_default_config_help()
        config_help.update({
            'host' : 'Hostname to collect from',
            'port' : 'Port to collect',
            'user' : 'Username',
            'password' : 'Password',

        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(HTTPRabbitMQCollector, self).get_default_config()
        config.update({
            'path': 'rabbitmq',
            'host': 'localhost',
            'port': '55672',
            'user': 'guest',
            'password': 'guest',
        })
        return config

    def collect(self):
        try:
            config = self.config
            if 'url' not in config:
                config['url'] = "http://%(host)s:%(port)s/api/queues" % config
                config['auth'] = ('%(user)s' % config,
                                  '%(password)s' % config)
            r = requests.get(config['url'],
                             auth=config['auth'],
                             headers=self.HTTP_HEADERS)
            if r.status_code != 200:
                raise ValueError("Cannot connect to RabbitMQ MGMT API")
            queues = json.loads(r.content)
            for queue in queues:
                for key in self.STATS:
                    self.publish('.'.join((queue['name'], key)), queue[key])
        except ValueError as e:
            self.log.error(str(e))
