import requests
import sys
import os
from pathlib import Path

file = Path(__file__).resolve()
sys.path.append(str(file.parent))

import publisher

def handle_cron(event, context):
    packages = os.environ['NPM_PACKAGES'].split(',')

    collect_npm_metrics(packages)

def collect_npm_metrics(packages):
    resp = requests.get('https://api.npmjs.org/downloads/point/last-day/{}'.format(
        ','.join(packages)
    ))
    if resp.status_code != 200:
        print('Error collecting metrics from NPM')
        raise Exception(resp.text)

    if len(packages) == 1:
        publisher.publish_metric(
            'npm.package.dailydownloads',
            resp.json().get('downloads', 0),
            tags=['package:{}'.format(packages[0])]
        )
    else:
        for key, value in resp.json().items():
            publisher.publish_metric(
                'npm.package.dailydownloads',
                value.get('downloads', 0),
                tags=['package:{}'.format(key)]
            )
