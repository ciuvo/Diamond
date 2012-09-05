import requests
import logging

try:
    import simplejson as json
except ImportError:
    import json

import diamond.collector

# disable requests logging
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.CRITICAL)


def nested_itemgetter(dict_, key):
    """Access a nested dict in dot notation.

    Example
    =======
    >>> d = {'foo': {'bar': 1}}
    >>> nested_itemgetter(d, 'foo.bar')
    1
    """
    keys = key.split('.')
    val = dict_
    for key in keys:
        val = val[key]
    return val


def split_list(token_string):
    """Split a list of colon seperated tokens. """
    tokens = filter(None, (t.strip() for
                           t in token_string.split(',')))
    return tokens


class HTTPRabbitMQCollector(diamond.collector.Collector):
    """A simple rabbitmq collector that uses the HTTP mgmt API."""

    HTTP_HEADERS = {"content-type": "application/json"}

    def get_default_config_help(self):
        config_help = super(HTTPRabbitMQCollector, self).get_default_config_help()
        config_help.update({
            'host': 'Hostname to collect from',
            'port': 'Port to collect',
            'user': 'Username',
            'password': 'Password',
            'queues': 'Queues to monitor; if None monitor all (default None)',
            'metric': 'Metrics to extract from each queue.',

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
            'queues': None,
            'metrics': 'memory,messages_ready,messages_unacknowledged,' \
                       'messages,consumers',
        })
        return config

    def collect(self):
        try:
            config = self.config

            # initialize config object on first collect.
            if 'url' not in config:
                config['url'] = "http://%(host)s:%(port)s/api/queues" % config
                config['auth'] = ('%(user)s' % config,
                                  '%(password)s' % config)
                metrics = split_list(config['metrics'])
                queues = split_list(config['queues'])
                config['metrics'] = frozenset(metrics)
                config['queues'] = frozenset(queues)

            # get stats from HTTP API
            r = requests.get(config['url'], auth=config['auth'],
                             headers=self.HTTP_HEADERS)
            if r.status_code != 200:
                raise ValueError("Cannot connect to RabbitMQ MGMT API")
            queues = json.loads(r.content)

            # publish metrics for each queue
            for queue in queues:
                queue_name = queue['name']
                if config['queues'] is None or queue_name in config['queues']:
                    for metric in config['metrics']:
                        try:
                            metric_name = '.'.join((queue['name'], metric))
                            metric_val = nested_itemgetter(queue, metric)
                            self.publish(metric_name, metric_val)
                        except KeyError as e:
                            self.log.warning("Cannot access metric '%s' "
                                             "in queue '%s'. %s", metric,
                                             queue_name, e)

        except ValueError as e:
            self.log.error(str(e))
        except requests.ConnectionError:
            self.log.error("Cannot connect to RabbitMQ mgmgt API. "
                           "Check if the mgmt plugin is enabled.")
