import requests
import sys
import os
from pathlib import Path
from functools import reduce

# nasty hack so we can import from the same dir/subdirs
file = Path(__file__).resolve()
sys.path.append(str(file.parent))

import publisher

BASE_URL = 'https://api.github.com'
GITHUB_TOKEN = os.environ['GITHUB_API_TOKEN']

AUTH_HEADER = {'Authorization': 'token {}'.format(GITHUB_TOKEN)}

def handle_cron(event, context):
    github_org = os.environ['GITHUB_ORG']
    collect_org_metrics(github_org)


def collect_org_metrics(org_name):
    resp = requests.get(BASE_URL + '/orgs/{}/repos'.format(org_name))
    if resp.status_code != 200:
        print('Error collecting metrics from GitHub!')
        raise Exception(resp.text)

    repos = map(lambda r: r['full_name'], resp.json())

    for repo in repos:
        collect_repo_metrics(repo)

def collect_repo_metrics(repo_name):
    publish_view_metrics(repo_name)
    publish_clone_metrics(repo_name)
    publish_release_download_metrics(repo_name)

def publish_view_metrics(repo_name):
    resp = requests.get(
        BASE_URL + '/repos/{}/traffic/views'.format(repo_name),
        headers=AUTH_HEADER
    )
    if resp.status_code != 200:
        print('Error collecting metrics for {}'.format(repo_name))
        raise Exception(resp.text)

    publisher.publish_metric(
        'github.repo.views',
        resp.json().get('uniques'),
        tags=['repo:{}'.format(repo_name)]
    )

def publish_clone_metrics(repo_name):
    resp = requests.get(
        BASE_URL + '/repos/{}/traffic/clones'.format(repo_name),
        headers=AUTH_HEADER
    )
    if resp.status_code != 200:
        print('Error collecting metrics for {}'.format(repo_name))
        raise Exception(resp.text)

    publisher.publish_metric(
        'github.repo.clones',
        resp.json().get('uniques'),
        tags=['repo:{}'.format(repo_name)]
    )

def publish_release_download_metrics(repo_name):
    resp = requests.get(
        BASE_URL + '/repos/{}/releases'.format(repo_name)
    )
    if resp.status_code != 200:
        print('Error collecting metrics for {}'.format(repo_name))
        raise Exception(resp.text)

    total_downloads = 0
    for release in resp.json():
        assets = release.get('assets', [])
        if assets:
            assets = release.get('assets', [])
            if assets:
                for asset in assets:
                    total_downloads += asset.get('download_count', 0)

    publisher.publish_metric(
        'github.repo.releasedownloads',
        total_downloads,
        tags=['repo:{}'.format(repo_name)]
    )
