"(it's free real estate)"

from __future__ import annotations

from contextlib import suppress
from itertools import product
from json import dump, load
from math import pi
from os import getenv
from os import path as os_path
from re import findall, search, sub
from sys import path as sys_path

from alive_progress import alive_bar
from dotenv import find_dotenv, load_dotenv
from pandas import DataFrame, notnull
from realestate_data.schematics import Filters, Locality, PriceRange, Search
from realestate_data.utils import paged_results
from requests.exceptions import ConnectionError

# metadata
__author__ = 'silvncr'
__license__ = 'MIT'
__module_name__ = 'realestatebot'
__version__ = '0.0.2'


# modes
is_debug = False
is_offline = False
number_of_postcodes = 0


# constants
degrees_to_km = 6371 * pi / 180


# debug function
def debug(*output: ...) -> None:
	'Outputs to console if debug mode is enabled.'
	if is_debug:
		print(' '.join(str(arg) for arg in [*output]))


# find keys function
def find_keys(obj: dict | list, key: str) -> ...:
	'Finds a key in a nested dictionary.'
	if isinstance(obj, dict):
		for k, v in obj.items():
			if k == key:
				return v
			if isinstance(v, (dict, list)):
				result = find_keys(v, key)
				if result is not None:
					return result
	elif isinstance(obj, list):
		for item in obj:
			result = find_keys(item, key)
			if result is not None:
				return result
	return None


# search function
def format_listings(r: list[dict]) -> list[dict | None]:
	'Formats search results into a list of dictionaries.'

	# format to list
	listings: list[dict | None] = []
	for page in r:
		for tier in page['tieredResults']:
			for result in tier['results']:
				price = None
				for listing in [result]:
					for f in [
						lambda x: find_keys(
							find_keys(find_keys(x, 'advertising'), 'display'),
							'display',
						),
						lambda x: find_keys(
							find_keys(find_keys(x, 'advertising'), 'price'),
							'display',
						),
						lambda x: find_keys(
							find_keys(find_keys(x, 'advertising'), 'priceRange'),
							'display',
						),
						lambda x: find_keys(
							find_keys(find_keys(x, 'advertising'), 'pricerange'),
							'display',
						),
						lambda x: find_keys(
							find_keys(find_keys(x, 'advertising'), 'priceText'),
							'display',
						),
						lambda x: find_keys(
							find_keys(find_keys(x, 'advertising'), 'pricetext'),
							'display',
						),
						lambda x: find_keys(find_keys(x, 'display'), 'display'),
						lambda x: find_keys(find_keys(x, 'price'), 'display'),
						lambda x: find_keys(find_keys(x, 'priceRange'), 'display'),
						lambda x: find_keys(find_keys(x, 'pricerange'), 'display'),
						lambda x: find_keys(find_keys(x, 'priceText'), 'display'),
						lambda x: find_keys(find_keys(x, 'pricetext'), 'display'),
						lambda x: find_keys(find_keys(x, 'advertising'), 'display'),
						lambda x: find_keys(find_keys(x, 'advertising'), 'price'),
						lambda x: find_keys(find_keys(x, 'advertising'), 'priceRange'),
						lambda x: find_keys(find_keys(x, 'advertising'), 'pricerange'),
						lambda x: find_keys(find_keys(x, 'advertising'), 'priceText'),
						lambda x: find_keys(find_keys(x, 'advertising'), 'pricetext'),
						lambda x: find_keys(x, 'display'),
						lambda x: find_keys(x, 'price'),
						lambda x: find_keys(x, 'priceRange'),
						lambda x: find_keys(x, 'pricerange'),
						lambda x: find_keys(x, 'priceText'),
						lambda x: find_keys(x, 'pricetext'),
					]:
						if f(listing):
							price = f(listing)
							break
						if price:
							break
					price = price or None
					listings.extend(
						[
							{
								'title': listing.get('title', {}),
								'address': listing.get('address', {}),
								'advertising': listing.get('advertising', {}),
								'features': listing.get('features', {}),
								'price': price,
							},
						],
					)

	# return search results
	return listings


# price function (parse string for low + high)
def parse_price(p: str) -> float:
	'Parses price string.'
	n = p or None

	# parse number
	try:
		n = float(n)  # type: ignore[]
	except (TypeError, ValueError):
		n = str(n).lower()
	else:
		debug('num:', p, '->', n)
		return n

	# expand abbreviations
	n = sub(
		r'f?r?o?m?\b\$?(\d+(\.\d+)?) ?k\b', lambda x: str(float(x.group()) * 1_000), n,
	)
	n = sub(
		r'f?r?o?m?\bk ?\$?(\d+(\.\d+)?)\b', lambda x: str(float(x.group()) * 1_000), n,
	)
	n = sub(
		r'f?r?o?m?\b\$?(\d+(\.\d+)?) ?m\b',
		lambda x: str(float(x.group()) * 1_000_000),
		n,
	)
	n = sub(
		r'f?r?o?m?\bm ?\$?(\d+(\.\d+)?)\b',
		lambda x: str(float(x.group()) * 1_000_000),
		n,
	)
	n = sub(
		r'f?r?o?m?\b\$?(\d+(\.\d+)?) ?b\b',
		lambda x: str(float(x.group()) * 1_000_000_000),
		n,
	)
	n = sub(
		r'f?r?o?m?\bb ?\$?(\d+(\.\d+)?)\b',
		lambda x: str(float(x.group()) * 1_000_000_000),
		n,
	)

	# parse string
	with suppress(Exception):
		m = [float(price.replace(',', '')) for price in findall(r'\$\s*([\d,]+)', n)]
		r = sum(m) / len(m)
		debug('str:', p, '->', n, '->', r)
		return r
	with suppress(Exception):
		r = float(search(r'\$\s*([\d,]+)', n).group().replace(',', ''))  # type: ignore[]
		debug('str:', p, '->', n, '->', r)
		return r
	for i, j in [
		('_', '-'),
		('k', '0' * 3),
		('m', '0' * 6),
		('b', '0' * 9),
		('p/w', ''),
		('p/m', ''),
		('p/a', ''),
		('p/y', ''),
		('$', ''),
		(',', ''),
		('+', ''),
		('!', ''),
		(' ', ''),
	]:
		n = n.lower().replace(i, j).lower()
	if '.' not in n:
		try:
			r = float(n)
		except ValueError:
			pass
		else:
			debug('str:', p, '->', n, '->', r)
			return r
	try:
		m = n.split('-')
		r = (float(m[0]) + float(m[1])) / 2
	except ValueError:
		pass
	else:
		if m[0] and m[1] and r:
			debug('str:', p, '->', n, '->', r)
			return r

	# matches no cases
	r = 0
	debug('nan:', p, '->', n, '->', r)
	return r


# distance function
def distance_from_target(
	lat: float, lon: float, target_lat: float | None, target_lon: float | None,
) -> float | None:
	'Calculates distance between two coordinates.'
	if not target_lat or not target_lon:
		debug('No target coordinates provided!')
		return None
	d = (
		(degrees_to_km * ((lat - target_lat) ** 2 + (lon - target_lon) ** 2) ** 0.5)
		if lat and lon
		else None
	)
	debug('Distance from', (target_lat, target_lon), 'to', (lat, lon), 'is', d, 'km')
	return d


# main function
def main(
	postcodes: set[str],
	states: set[str],
	price_range: tuple[float, float],
	target: tuple[float | None, float | None] = (0, 0),
) -> tuple[DataFrame, list[dict]]:
	'Runs the main function.'

	# target coordinates
	if not target[0]:
		target = (0, target[1])
	if not target[1]:
		target = (target[0], 0)

	# debug
	debug(
		'\nPostcodes:',
		postcodes,
		'\nStates:',
		states,
		'\nPrice Range:',
		price_range,
		'\nTarget:',
		target,
	)

	# offline mode
	if is_offline:
		# load data from raw.json
		print("\n\tOffline mode: loading from 'raw.json'..")
		with open(os_path.join(sys_path[0], 'raw.json'), 'tr') as file:
			raw_listings = extra_raw_listings = load(file)

	# online mode
	else:
		# price range
		_pricerange = PriceRange()
		_pricerange.minimum = price_range[0] or 10_000  # type: ignore[]
		_pricerange.maximum = price_range[1] or 10_000_000  # type: ignore[]

		# locality filters
		_locality = Locality()
		_locality.locality = ''  # type: ignore[]
		try:
			_locality.subdivision = next(iter(states))  # type: ignore[]
		except (ValueError, StopIteration):
			_locality.subdivision = Locality.SUBDIVISION_ACT  # type: ignore[]
		try:
			_locality.postcode = int(next(iter(postcodes)))  # type: ignore[]
		except (ValueError, StopIteration):
			_locality.postcode = ''  # type: ignore[]

		# search filters
		_filters = Filters()
		_filters.property_types = list(Filters.PROPERTY_TYPE_CHOICES)  # type: ignore[]
		_filters.surrounding_suburbs = True  # type: ignore[]
		_filters.minimum_bedrooms = 1  # type: ignore[]
		_filters.minimum_bathrooms = 1  # type: ignore[]
		_filters.minimum_parking_spaces = 1  # type: ignore[]
		_filters.price_range = _pricerange  # type: ignore[]

		# search object
		_search = Search()
		_search.channel = Search.CHANNEL_SOLD  # type: ignore[]
		_search.localities = [_locality]  # type: ignore[]
		_search.filters = _filters  # type: ignore[]
		_search.validate()

		# search with filters
		print('')
		raw_listings = []
		extra_raw_listings = []
		with alive_bar(
			(
				0
				if any([postcodes == ('',), states == ('',)])
				else len(postcodes) * len(states)
			),
			title='Searching..',
			title_length=12,
		) as bar:
			for _postcode, _ in product(postcodes, states):
				call_succeeded = False
				i = 0
				while not call_succeeded:
					try:
						try:
							_search.localities[0].postcode = int(_postcode)  # type: ignore[]
						except ValueError:
							break
						_search.localities[0].state = Locality.SUBDIVISION_QLD  # type: ignore[]
						bar.text(
							f'| ({_search.localities[0].subdivision}, '  # type: ignore[]
							f'{_search.localities[0].postcode})',  # type: ignore[]
						)
						r = list(paged_results(_search))
						raw_listings.extend(format_listings(r))
						extra_raw_listings.extend(r)
					except ConnectionError:
						i += 1
						bar.text(
							f'| ({_search.localities[0].subdivision},'  # type: ignore[]
							f' {_search.localities[0].postcode})',  # type: ignore[]
							f'[{i}]' if i else '',
						)
					else:
						call_succeeded = True
				if call_succeeded:
					bar()

	# format results
	if not raw_listings:
		return DataFrame(), []
	if len(raw_listings) != 0:
		debug('')
	formatted_listings = []
	with alive_bar(len(raw_listings), title='Formatting..', title_length=12) as bar:
		for listing in raw_listings:
			address = (
				sub(
					r'\bSt\b', 'Street',
					listing
						.get('address', {})
						.get('streetAddress'),
				)
				if listing.get('address', {}).get('streetAddress') is not None
				else None
			) or None
			_postcode = (
				listing.get('address', {}).get('postcode')
				or listing.get('address', {}).get('postCode')
			) or None
			bedrooms = int(
				(
					listing.get('features', {}).get('general', {}).get('bedrooms')
					or int(
						listing.get('generalFeatures', {})
						.get('bedrooms', {})
						.get('value', 0),
					)
				)
				or 0,
			)
			bathrooms = int(
				(
					listing.get('features', {}).get('general', {}).get('bathrooms')
					or int(
						listing.get('generalFeatures', {})
						.get('bathrooms', {})
						.get('value', 0),
					)
				)
				or 0,
			)
			parking = int(
				(
					listing.get('features', {}).get('general', {}).get('parkingSpaces')
					or int(
						listing.get('generalFeatures', {})
						.get('parkingSpaces', {})
						.get('value', 0),
					)
				)
				or 0,
			)
			latitude = (
				float(listing.get('address', {}).get('location', {}).get('latitude', 0))
				or None
			)
			longitude = (
				float(
					listing.get('address', {}).get('location', {}).get('longitude', 0),
				)
				or None
			)
			distance = (
				distance_from_target(
					latitude or 0, longitude or 0, target[0] or None, target[1] or None,
				)
				or 0
			)
			price = parse_price(listing.get('price'))
			if all(
				[
					(price_range[0] <= price <= price_range[1])
					or (not price_range[0] and not price_range[1]),
					(latitude and longitude and distance)
					or (not target[0] and not target[1]),
				],
			):
				formatted_listings.extend(
					[
						{
							'address': address,
							'postcode': _postcode,
							'bedrooms': bedrooms,
							'bathrooms': bathrooms,
							'parking': parking,
							'latitude': latitude,
							'longitude': longitude,
							'distance_km': distance,
							'price_aud': price,
						},
					],
				)
				bar()

	# create dataframe
	data = DataFrame(formatted_listings) if formatted_listings else DataFrame()

	# drop null values
	if target[0] and target[1]:
		for name in ['distance_km', 'price_aud']:
			if name in data.columns:
				data = data.dropna(subset=[name])

	# drop duplicates
	data = data.drop_duplicates(subset=['address'])
	data = data.where(notnull(data), None)

	# return
	return data, extra_raw_listings


# run main
if __name__ == '__main__':
	# set environment variables
	load_dotenv(find_dotenv())
	POSTCODES: set[str] = {str(i) for i in str(getenv('POSTCODES')).split(',')}
	STATES: set[str] = {str(i) for i in str(getenv('STATES')).split(',')}
	TARGET_LAT: float | None = float(getenv('TARGET_LAT', None) or 0) or None
	TARGET_LON: float | None = float(getenv('TARGET_LON', None) or 0) or None
	PRICE_LOW: float = float(getenv('PRICE_LOW', None) or 10_000)
	PRICE_HIGH: float = float(getenv('PRICE_HIGH', None) or 10_000_000)

	# run main function
	data, raw = main(
		set(list(POSTCODES)[: (number_of_postcodes or len(POSTCODES))]),
		STATES,
		(PRICE_LOW, PRICE_HIGH),
		(TARGET_LAT, TARGET_LON),
	)
	processed_listings = data.to_dict(orient='records')

	# save search results
	if is_debug:
		with open(os_path.join(sys_path[0], 'raw.json'), 'w', encoding='utf-8') as file:
			dump(raw, file, indent=4)

	# save listings
	with open(os_path.join(sys_path[0], 'out.csv'), 'w', encoding='utf-8') as file:
		data.to_csv(file, index=False)
	with open(os_path.join(sys_path[0], 'out.csv'), encoding='utf-8') as file:
		content = file.read()
	content = content.replace('\n\n', '\n')
	with open(os_path.join(sys_path[0], 'out.csv'), 'w', encoding='utf-8') as file:
		file.write(content)

	# print search results
	print('\n\tExported', len(processed_listings), 'listings!')
