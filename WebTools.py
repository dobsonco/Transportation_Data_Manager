from urllib.request import urlopen
from bs4 import BeautifulSoup
import signal

# Creating timeout error to limit the runtime of a function if needed
class TimeoutException(Exception): # Creating custom error
    pass

def timeout_handler(): # Creating function to handle error
    print('Reached maximum allotted time')
    raise TimeoutException
    
signal.signal(signal.SIGALRM, timeout_handler);

def get_title(url):
    '''
    This function reads the html and finds the title, returning it as a string
    '''
    if (url == None) or ('http' not in url):
        raise ValueError(f'Not a useable url: "{url}"')
    try:
        response = urlopen(url)
        soup = BeautifulSoup(response, 'html.parser')
        title = soup.title.get_text()
        del url,soup,response
        return title
    except:
        raise ValueError(f'Not a useable url: "{url}"')
    
def find_all_links(page):
    '''
    Finds all links on page, this is a WIP as it doesn't find all links
    '''
    soup = BeautifulSoup(page,features="lxml")
    all_links = []
    for line in soup.find_all('a'):
        line = line.get('href')
        try:
            if ('http' not in line):
                continue
        except:
            continue
        all_links.append(line)
    del soup,line,page
    return list(set(all_links))

def find_relevant_links_and_titles(all_links,keywords,search_title = False):
    '''
    Given a list of links and a list of keywords this method will find links/titles that contain
    keywords

    all_links: list, contains all links you want to parse

    keywords: list, contains all keywords you want to look for

    search_title: bool, leave this set to false in order to save time, but if you want to search
        titles anyway, set it to true. If set to true, the script will download the html
        of the page, strip the title from it, and then look for keywords. This is a massive
        time waste.
    '''
    name_and_link = []
    keywords_upper = [string.capitalize() for string in keywords]
    for link in all_links:
        signal.alarm(5)
        if search_title:
            try:
                title = get_title(link).lower()
                if any(substring in title for substring in keywords):
                    name_and_link.append((title,link)) 
                else:
                    pass
            except:
                continue
            else: 
                signal.alarm(0)
        else:
            try:
                link = link.lower()
                if any(substring in link for substring in keywords):
                    title = get_title(link)
                    name_and_link.append((title,link))
                else:              
                    pass
            except:
                continue
            else:
                signal.alarm(0)
    del keywords,keywords_upper,link,all_links
    return list(set(name_and_link))

def relevant_links(url,keywords):
    '''
    This method takes a link, strips all links on the page, and finds all links that contain
    keywords

    url: string, link to website you want to parse

    keywords: list, contains all keywords to look for

    returns: list of links that match
    '''

    page = urlopen(url).read()

    all_links = find_all_links(page)

    name_and_link = list(set(find_relevant_links_and_titles(all_links,keywords,search_title=False)))

    return name_and_link