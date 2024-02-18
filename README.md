# realestatebot

uses [`realestate-data`](https://github.com/storerjeremy/realestate-data) to gather listings from the `realestate.com.au` api

## setup

`.env` (example)

note: no token is required for the api

```sh
    # comma-separated lists

postcodes="2600,2601,2602"          # main search parameter
states="ACT,NSW,VIC,QLD,NT,SA,TAS"  # WA is not supported by the api (not sure why)

    # target location (for distance calculations)

target_lat=-35.5222  # latitude
target_lon=149.0808  # longitude
```

## run

clone the repository and install the requirements

```sh
git clone https://github.com/silvncr/realestatebot.git
cd realestatebot
pip install -r requirements.txt

    # make sure to set up `.env` before running

python realestatebot/__init__.py
```

## library

this is a library, so you can use it in your own projects

```sh
pip install realestatebot
```

try it yourself with this example

```python
from json import dump
from os   import path as os_path
from sys  import path as sys_path

from realestatebot import main

with open(os_path.join(sys_path[0], 'out.json'), 'w') as file:
    dump(main(

        postcodes   = [2600],
        states      = ['ACT'],
        target      = (-35.5222, 149.0808),
        price_range = (10_000, 10_000_000),

    )[0].to_dict(orient="records"), file, indent=4)

print('\ndone')
```

## todo

| feature | basic | better | finished |
|---|:-:|:-:|:-:|
| code comments | ✔️ | | |
| code quality | | ✔️ | |
| documentation | ✔️ | | |
| error handling | ✔️ | | |
| examples | ✔️ | | |
| logging | ✔️ | | |
| modulation | ✔️ | | |
| output formats | ✔️ | | |
| performance | | ✔️ | |
| reliability | ✔️ | | |
| search parameters | ✔️ | | |
| security | | ✔️ | |
| tests | ✔️ | | |
