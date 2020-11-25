# ----------------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------------
import requests
import logging
import os
import json
from time import sleep, time
import json
import random
import datetime
import re

# ----------------------------------------------------------------------------------
# Class
# ----------------------------------------------------------------------------------
class ScryfallAPI:
    def __init__(self):
        self.url = 'https://api.scryfall.com'
        self.cache = dict()

        # Get a list of files in the working directory
        files = [file for file in os.listdir('.') if os.path.isfile(file)]
        pattern = r'^default-cards-(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)'
        database_file = None

        # Check all the files names to see if we have a default-cards file
        for file in files:
            # Check to see if we have a recent default-cards file
            match = re.match(pattern, file)
            if match:
                now = datetime.datetime.now()
                file_date = match.groupdict()
                if str(now.year) == file_date['year'] and \
                   str(now.month) == file_date['month'] and \
                   str(now.day) == file_date['day']:
                    database_file = file
                    break
                else:
                    # Remove old database files
                    os.remove(file)

        # If a database file is not present, get the latest database file from the API
        if not database_file:
            database_file = self.get_bulk_data()
            if not database_file:
                raise('Failed to open database file')

        self.database = None
        self.database_size = 0
        with open(file=database_file, encoding="utf8") as file:
            file_data = file.read()
            self.database = json.loads(file_data)
            self.database_size = len(self.database)

    # ------------------------------------------------------------------------
    def _response_to_json(self, response):
        raw = None
        try:
            raw = response.json()
        except:
            pass
        return raw

    # ------------------------------------------------------------------------
    def get_bulk_data(self, type='default_cards'):
        sleep(0.25)

        # Ask scryfall for bulk data
        request = '{url}/bulk-data'.format(url=self.url)
        response = requests.get(url=request)
        raw = self._response_to_json(response)

        # Parse the bulk data from scryfall
        if response.ok and raw:
            download = None
            for bulk in raw['data']:
                # Search for the bulk data type we want
                if bulk['type'] == type:
                    # Save the download link and exit the loop
                    download = bulk['download_uri']
                    break

            # Check if we found the download link
            if download:
                # Download the bulk data file
                bulk_file = requests.get(download)
                if bulk_file.ok:
                    try:
                        # Create a new default-cards file and write the downloaded data to the file
                        now = datetime.datetime.now()
                        database_file = 'default-cards-{year}-{month}-{day}.json'.format(year=now.year, month=now.month, day=now.day)
                        with open(database_file, 'wb') as file:
                            file.write(bulk_file.content)
                        return database_file
                    except IOError as e:
                        print("Couldn't open or write to file (%s)." % e)
        return None

    # ------------------------------------------------------------------------
    def get_card(self, card, expansion=None):
        if card in self.cache:
            return self.cache[card]

        # Required API wait
        sleep(0.2)

        # Request with the set if it was given
        if expansion:
            request = '{url}/cards/named?exact={cardName}&set={expansion}'.format(url=self.url, cardName=card, expansion=expansion.lower())
        else:
            request = '{url}/cards/named?exact={cardName}'.format(url = self.url, cardName = card)

        response = requests.get(request)
        raw = self._response_to_json(response)

        if response.ok and raw:
            self.cache[card] = raw

        return raw

    # ------------------------------------------------------------------------
    def get_card_price(self, card, expansion=None, price='usd'):
        data = self.get_card(card, expansion)

        price = data['prices'][price]

        return price

    # ------------------------------------------------------------------------
    def get_card_rarity(self, card, expansion=None):
        data = self.get_card(card, expansion)

        if data:
            rarity = data['rarity']
        else:
            rarity = 'unknown'

        return rarity

    # ------------------------------------------------------------------------
    def get_random_card_from_database(self):
        if self.database:
            index = random.randint(0, self.database_size - 1)
            return self.database[index]


#api.get_bulk_data()
#api.get_card('Monastery Swiftspear')
#api.get_card('Uro, Titan of Nature\'s Wrath')
#lotus = api.get_card('Black Lotus', '2ED')
#bolt = api.get_card('Lightning Bolt')

# start = time()
# for i in range(0,1000):
#     print(api.get_random_card_from_database())
# end = time()
# print(end-start)
#
#
# for i in range(0, len(api.database)):
#     if api.database[i]['name'] == 'Mogg Fanatic':
#         print(str(api.database[i]['games']) + ', ' + str(api.database[i]['expansion']) + ', ' + str(api.database[i]['prices']))
#
# pass
