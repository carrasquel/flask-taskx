from urllib.parse import urlparse


def get_scheme(url):
    parsed_uri = urlparse(url)

    return parsed_uri.scheme
