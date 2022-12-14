# mastodon_list_importer
Mastodon list importer python script

This is the basic infrastructure for a list importer python script.
Right now it looks like it's only working with 4.x servers.

## Requirements
Python 3.x
Mastodon.py installed from: https://github.com/halcy/Mastodon.py

## Install/Getting Started

```
# Create a pyenv
python3 -m venv mastodon_env
cd mastodon_env
source bin/activate
pip3 install Mastodon.py
cd <list importer repo>

# Help listing
./list_importer.py --help
usage: list_importer.py [-h] -s SERVER -u USER -l LIST [-i] [-t] csv_input

Import a CSV file into a mastodon list.

positional arguments:
  csv_input             Input CSV file

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Target server
  -u USER, --user USER  Login name (usually an e-mail address)
  -l LIST, --list LIST  Target list name
  -i, --ignore_version_check
                        Ignore the Mastodon server version check (useful for communicating with Mastodon forks like
                        Hometown which may have a differently formatted version string
  -t, --testing         Test mode. Accounts will not be followed and added to the list, but the list will be
                        created
```

