# built-in
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, Iterator, List

import requests
import gnupg

DEFAULT_KEYSERVER = 'pgp.mit.edu'
JSON_URL = 'https://pypi.org/pypi/{path}/json'
logger = getLogger(__package__)


def get_urls(name: str, version: str) -> List[str]:
    path = f'{name}/{version}' if version else name
    url = JSON_URL.format(path=path)
    response = requests.get(url=url)
    response.raise_for_status()
    files = response.json()['urls']
    return [finfo['url'] for finfo in files]


def verify_release(urls: List[str], gpg: gnupg.GPG) -> Iterator[Dict[str, Any]]:
    with TemporaryDirectory() as root_path:
        for url in urls:
            name = url.rsplit('/', maxsplit=1)[-1]

            # download signature file
            sign_path = Path(root_path) / 'archive.bin.asc'
            response = requests.get(url + '.asc')
            if response.status_code == 404:
                yield dict(
                    status='no signature found',
                    name=name,
                )
                continue
            response.raise_for_status()
            sign_path.write_bytes(response.content)

            # download release file
            response = requests.get(url)
            if response.status_code == 404:
                yield dict(
                    status='release not found',
                    name=name,
                )
                continue
            response.raise_for_status()

            info = _verify_data(
                gpg=gpg,
                sign_path=sign_path,
                data=response.content,
            )
            info['name'] = name
            yield info


def _verify_data(
    gpg: gnupg.GPG,
    sign_path: Path,
    data: bytes,
    retry: bool = True,
) -> Dict[str, Any]:
    verif = gpg.verify_data(str(sign_path), data)
    result = dict(
        created=verif.creation_date,
        fingerprint=verif.fingerprint,
        key_id=verif.key_id,
        status=verif.status,
        username=verif.username,
    )

    if verif.status == 'no public key' and retry:
        # try to import keys and verify again
        logger.debug('searching the key...', extra=dict(key_id=verif.key_id))
        keys = gpg.search_keys(query=verif.key_id, keyserver=DEFAULT_KEYSERVER)
        if len(keys) != 1:
            logger.debug('cannot find the key', extra=dict(
                count=len(keys),
                key_id=verif.key_id,
            ))
            return result
        gpg.recv_keys(DEFAULT_KEYSERVER, keys[0]['keyid'])
        return _verify_data(gpg=gpg, sign_path=sign_path, data=data, retry=False)

    return result
