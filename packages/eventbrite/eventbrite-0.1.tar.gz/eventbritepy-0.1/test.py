#!/usr/bin/env python

import eventbrite
import pprint

pp = pprint.PrettyPrinter(indent = 4)

api = eventbrite.API('your_api_key', cache='.cache')
events = api.call('event_search', city='San Francisco')

for event in events['events']:
    pp.pprint(event)

