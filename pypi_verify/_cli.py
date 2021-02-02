import json
import sys
from argparse import ArgumentParser
from typing import Any, Dict, List, NoReturn, TextIO

import gnupg

from ._core import get_urls, verify_release


def main(argv: List[str], stream: TextIO = sys.stdout) -> int:
    parser = ArgumentParser()
    parser.add_argument('packages', nargs='+')
    args = parser.parse_args(argv)

    gpg = gnupg.GPG()
    json_params: Dict[str, Any] = dict(
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    invalid = 0

    pkg: str
    for pkg in args.packages:
        name, _, version = pkg.partition('==')
        if not name:
            print('package name required', file=stream)
            return 1
        urls = get_urls(name=name, version=version)
        infos = verify_release(urls=urls, gpg=gpg)

        for info in infos:
            if info['status'] != 'signature valid':
                invalid += 1
            print(json.dumps(info, **json_params), file=stream)
    return invalid


def entrypoint() -> NoReturn:
    sys.exit(main(argv=sys.argv[1:]))
