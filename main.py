import random
import re

import requests
from bs4 import BeautifulSoup
import twitter
import os
import pickle

SAVE_DATA_FILE = "band_names_dict.p"
BAND_NAMES_URL = 'https://en.wikipedia.org/wiki/List_of_band_name_etymologies'
LAST_HEADING = 'See also[edit]'


def process_text(text):
    # Remove references example: [1]
    text_no_references = re.sub(r'\[.*?\]', "", text)
    return text_no_references


# Returns a list of headers on a Wikipedia page
def scrape_list_article(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    section_headings = soup.find_all('h2')
    print(section_headings)
    heading_dict = {}
    for heading in section_headings:
        print(heading.text)
        section_list_tag = heading.find_next_sibling("ul")
        if not section_list_tag or heading.text == LAST_HEADING:
            break
        section_items = section_list_tag.children
        ls_section_tags = list(section_items)
        section_items = [process_text(item.text) for item in ls_section_tags if item != '\n']
        heading_dict[heading.text] = section_items
    return heading_dict


def main():
    if os.path.exists(SAVE_DATA_FILE):
        with open(SAVE_DATA_FILE, 'rb') as f:
            headings_to_list = pickle.load(f)
    else:
        html = requests.get(BAND_NAMES_URL)
        headings_to_list = scrape_list_article(html.text)

    heading = random.choice(list(headings_to_list.keys()))
    band_etymology = random.choice(headings_to_list[heading])
    headings_to_list[heading].remove(band_etymology)
    print(band_etymology)

    total = 0
    for heading in headings_to_list:
        total += len(headings_to_list[heading])
    print(total)

    with open(SAVE_DATA_FILE, 'wb') as f:
        pickle.dump(headings_to_list, f)

    api = twitter.Api(consumer_key=os.getenv("BANDS_CONSUMER_KEY"),
                      consumer_secret=os.getenv("BANDS_CONSUMER_SECRET"),
                      access_token_key=os.getenv("BANDS_ACCESS_TOKEN_KEY"),
                      access_token_secret=os.getenv("BANDS_ACCESS_TOKEN_SECRET"))
    api.PostUpdate(band_etymology)


if __name__ == "__main__":
    main()
