# vpypi

**vpypi** is a CLI tool to verify [GPG](https://gnupg.org/) signature for Python packages on [PyPI](http://pypi.org/).

## Installation

```bash
python3 -m pip install --user vpypi
```

## Usage

```bash
$ python3.9 -m vpypi flask==1.1.1
{
  "created": "2019-07-08",
  "fingerprint": "AD253D8661D175D001F462D77A1C87E3F5BC42A8",
  "key_id": "7A1C87E3F5BC42A8",
  "name": "Flask-1.1.1-py2.py3-none-any.whl",
  "status": "signature valid",
  "username": "David Lord <davidism@gmail.com>"
}
{
  "created": "2019-07-08",
  "fingerprint": "AD253D8661D175D001F462D77A1C87E3F5BC42A8",
  "key_id": "7A1C87E3F5BC42A8",
  "name": "Flask-1.1.1.tar.gz",
  "status": "signature valid",
  "username": "David Lord <davidism@gmail.com>"
}
```
