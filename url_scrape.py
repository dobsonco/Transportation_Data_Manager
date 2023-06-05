from urllib.request import urlopen
import re
from bs4 import BeautifulSoup
import signal
import WebTools as WT
Tools = WT.Tools()

def main():
    page = urlopen("https://chcrpa.org/data-and-analyses/data/").read()

    all_links = Tools.find_all_links(page)

    keywords = ['transport','car','train','railroad','vehicle','fuel','travel','port','road',
                'highway','bridge','bus','electric vehicle','airport','transit','sidewalk',
                'bike','sidewalk','traffic']
    name_and_link = Tools.find_relevant_links_and_titles(all_links,keywords,search_title=False)

    print(set(name_and_link))

if __name__ == '__main__':
    main()
