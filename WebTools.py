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

class Tools:

    def get_title(self,url):
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
        
    def find_all_links(self,page):
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
    
    def find_relevant_links_and_titles(self,all_links,keywords,search_title = False):
        name_and_link = []
        keywords_upper = [string.capitalize() for string in keywords]
        for link in all_links:
            signal.alarm(5)
            if search_title:
                try:
                    title = self.get_title(link).lower()
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
                        title = self.get_title(link)
                        name_and_link.append((title,link))
                    else:              
                        pass
                except:
                    continue
                else:
                    signal.alarm(0)
        del keywords,keywords_upper,title,link,all_links
        return list(set(name_and_link))