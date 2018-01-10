#!/usr/bin/env python
"""
Given the URL of a Thing page on Thingiverse this script downloads the Thing's
3D models
"""

# TODO add URL to model JSON
# TODO add license to model JSON

import sys
import os
import json
from urlparse import urlparse
from bs4 import BeautifulSoup
import requests

def die_with_usage():
    """ Print usage of program and then exit with error """
    print 'Usage: {} <thing URL>'.format(sys.argv[0] or '')
    sys.exit(1)

def download_thing_page(url):
    """ GET the HTML content of a page or raise an Exception """
    req = requests.get(url)

    if req.status_code == 200:
        return req.text
    else:
        raise Exception('Request for Thing page failed with status code {}'.format(req.status_code))

def find_thing_models(url):
    """ Retrieve the links to 3D models on a Thing page """
    thing_view_attr = 'data-thingiview-url'

    thing_page = download_thing_page(url)
    soup = BeautifulSoup(thing_page, 'html.parser')
    thing_view_tags = soup.findAll(lambda tag: thing_view_attr in tag.attrs)

    thing_view_urls = []
    for thing_view_tag in thing_view_tags:
        thing_view_urls += [thing_view_tag.attrs[thing_view_attr]]

    unique_urls = list(set(thing_view_urls))

    return filter(None, unique_urls)

def model_name(url):
    """ Takes the URL of a Thingiverse threejs_json file and returns the name """
    unique_id_len = 8
    ext_len = 3 # Length of '.js'
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    if len(filename) > (unique_id_len + ext_len):
        return filename[8:-3]
    else:
        raise Exception('Model has unexpectedly short name "{}"'.format(filename))

def download_things(url, directory='./'):
    """ Retrieve the 3D models linked from a Thing page """

    if not os.path.isdir(directory):
        raise Exception('Cannot download to nonexistent directory "{}"'.format(directory))

    model_urls = find_thing_models(url)

    for model_url in model_urls:
        name = model_name(model_url)
        req = requests.get(model_url)

        if not req.status_code == 200:
            raise Exception('Download of {} failed with status code {}'.format(name, req.status_code))

        try:
            model_json = req.json()
        except ValueError as err:
            print 'Failed to download {} because {}'.format(name, str(err))

        model_path = os.path.join(directory, '{}.json'.format(name))

        # TODO handle case of model with same name already existing
        with open(model_path, 'w') as model_file:
            model_file.write(json.dumps(model_json, indent=4))

def main():
    """ Entrypoint """

    if len(sys.argv) != 2:
        die_with_usage()

    url = sys.argv[1]

    download_things(url, './models')

main()
