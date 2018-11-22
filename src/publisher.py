# Lambda custom metric collection
# https://docs.datadoghq.com/integrations/amazon_lambda/#lambda-metrics

import time

def publish_metric(name, value, tags=[], metric_type='count'):
    log_string = 'MONITORING|{}|{}|{}|{}'.format(
        int(time.time()), value, metric_type, name
    )
    if tags:
        log_string = log_string + '|#{}'.format(','.join(tags))

    print(log_string)
