# realestatebot

uses [`realestate-data`](https://github.com/storerjeremy/realestate-data) to gather listings from the [realestate.com.au](https://realestate.com.au) "api" (not really an api, but it works)

> notes:
>
> - no "token" is required as it basically rips from the website
> - deviating too far from the examples counts as misuse, and may cause unpredicatable behaviour

## setup

```sh
git clone https://github.com/silvncr/realestatebot.git
```

`.env` (example)

```sh
    # comma-separated lists; no spaces; make sure to set these up

postcodes="2600,2601,2602"         # main search parameter
states="ACT,NSW,VIC,QLD,NT,SA,TAS"  # WA is not supported (not sure why)

    # target location (for distance calculations); not required, can be left empty

target_lat=35.5222  # latitude
target_lon=149.0808  # longitude
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

        postcodes   = [2600],
        states      = ['ACT'],
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
