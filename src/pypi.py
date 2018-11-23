import requests
import sys
import os
from pathlib import Path

file = Path(__file__).resolve()
sys.path.append(str(file.parent))

import publisher

def handle_cron(event, context):
    packages = os.environ['PYPI_PACKAGES'].split(',')

    collect_pypi_metrics(packages)


def collect_pypi_metrics(packages):
    for package in packages:
        resp = requests.get('https://pypistats.org/api/packages/{}/recent'.format(package))
        if resp.status_code != 200:
            print('Error collecting metrics from PyPi')
            raise Exception(resp.text)

        stats = resp.json().get('data', {})

        publisher.publish_metric(
            'pypi.package.dailydownloads',
            stats.get('last_day', 0),
            tags=['package:{}'.format(package)]
        )
        publisher.publish_metric(
            'pypi.package.weeklydownloads',
            stats.get('last_week', 0),
            tags=['package:{}'.format(package)]
        )
        publisher.publish_metric(
            'pypi.package.monthlydownloads',
            stats.get('last_month', 0),
            tags=['package:{}'.format(package)]
        )
