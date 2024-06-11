# realestatebot

tool for ripping Australian real estate listings

![version](https://img.shields.io/pypi/v/realestatebot)
![status](https://img.shields.io/github/actions/workflow/status/silvncr/realestatebot/python-publish.yml)
![downloads](https://img.shields.io/pypi/dm/realestatebot)

![license](https://img.shields.io/github/license/silvncr/realestatebot)
![python](https://img.shields.io/pypi/pyversions/realestatebot)

## summary

uses [`realestate-data`](https://github.com/storerjeremy/realestate-data) to rip listings from [realestate.com.au](https://realestate.com.au)

this module has not been properly tested, and as such, deviating too far from the examples counts as misuse, and may cause unpredicatable behaviour

i made this for personal use, and i'm sharing it in case someone else finds it useful

## setup

```sh
git clone https://github.com/silvncr/realestatebot.git
```

`.env` (example)

```sh
    # comma-separated lists; no spaces; required

POSTCODES="2600,2601,2602"         # main search parameter; more can be added
STATES="ACT,NSW,VIC,QLD,NT,SA,TAS"  # WA is not supported (not sure why)

    # target location (for distance calculations); not required, can be omitted

# idk where this is btw
TARGET_LAT=-35.308056  # latitude (in decimal degrees north)
TARGET_LON=149.124444  # longitude (in decimal degrees east)

    # price range (in AUD); not required, can be omitted; defaults shown below

PRICE_MIN=10000    # minimum price; not validated in-app; can be zero
PRICE_MAX=10000000  # maximum price; not validated in-app
```

## run

```sh
cd realestatebot

    # make sure to set up `.env` before running

pip install -r requirements.txt
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

        postcodes   = {2600},
        states      = {'ACT'},
        target      = (35.5222, 149.0808),
        price_range = (10_000, 10_000_000),

    )[0].to_dict(orient="records"), file, indent=4)

print('\ndone')
```

## todo

| feature           | basic | better | finished |
| ----------------- | :---: | :----: | :------: |
| code comments     |   x   |        |          |
| code quality      |       |   x    |          |
| documentation     |   x   |        |          |
| error handling    |   x   |        |          |
| examples          |   x   |        |          |
| logging           |   x   |        |          |
| modulation        |   x   |        |          |
| output formats    |   x   |        |          |
| performance       |       |   x    |          |
| reliability       |   x   |        |          |
| search parameters |   x   |        |          |
| security          |       |   x    |          |
| tests             |   x   |        |          |
