from ..configs.secrets import BING_API_KEY
from ..configs.settings import SETTINGS
import requests
import sys
import json

"""

To integrate a new search engine API, implement the SearchEngine class.

The main functions return SearchResult or ImageSearchResult objects.

"""

class SearchResult():
    name: str
    url: str
    language: str  # A code, like en
    snippet: str
    def __init__(self, name, url, language="", snippet="") -> None:
        self.name = name
        self.url = url
        self.language = language
        self.snippet = snippet
    def to_json(self):
        return {
            'name': self.name,
            'url': self.url,
            'language': self.language,
            'snippet': self.snippet
        }


class SearchEngine():
    def __init__(self, engine, code, name, desc, traits, use_pdf, market) -> None:
        self.engine = engine
        self.code = code
        self.name = name
        self.desc = desc
        self.traits = traits
        self.use_pdf = use_pdf
        self.market = market

    # Returns (list[SearchResult], total)
    def search(self, query, max_n=10, offset=0):
        raise Exception(f"Search not implemented for search engine with code '{self.code}'")
    
    def to_json_obj(self):
        return {
            'engine': self.engine,
            'code': self.code,
            'name': self.name,
            'desc': self.desc,
            'traits': self.traits,
            'use_pdf': self.use_pdf
        }


class Bing(SearchEngine):
    
    def search(self, query, max_n=10, offset=0):
        endpoint = "https://api.bing.microsoft.com/v7.0/search"
        # Refer here for bing market codes:  https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/market-codes
        mkt = 'en-US' if not self.market else self.market
        params = { 'q': query, 'mkt': mkt, 'count': max_n, 'offset': offset }  # count defaults to 10, can be up to 50
        headers = { 'Ocp-Apim-Subscription-Key': BING_API_KEY }
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()  # will throw an error if the request isn't good
        my_json = response.json()
        try:
            total = my_json['webPages']['totalEstimatedMatches']
            raw_results = my_json['webPages']['value']
        except:
            print(f"Could not get web pages from search engine. Here was the repsonse: {my_json}", file=sys.stderr)
            return []
        
        results = [SearchResult(x['name'], x['url'], language=x['language'], snippet=x['snippet']) for i, x in enumerate(raw_results) if i < max_n]
        return results, total


class SearXNG(SearchEngine):

    def search(self, query, max_n=10, offset=0):
        # TODO: add support for different market/language etc codes
        
        # Since there's no offset or limit in the SearXNG API, we have to convert to pages
        page = 1 + (offset // max_n)
        params = {'q': query, 'format': 'json', 'pageno': page}
        url = SETTINGS['searxng']['url']
        if self.engine:
            params['engines'] = self.engine
        response = requests.get(f"{url}/search", params=params)
        my_json = response.json()
        if 'error' in my_json:
            e = my_json['error']
            raise Exception(f"Error trying SearXNG: {e}")
        results = my_json['results']
        result_objs = []
        for i, res in enumerate(results):
            if i >= max_n:
                break
            # Using the PDF url instead of the regularly URL can be useful for scholarly works
            if self.use_pdf:
                if 'pdf_url' in res and res['pdf_url']:
                    result_objs.append(SearchResult(res['title'], res['pdf_url'], snippet=res['content']))
                else:
                    result_objs.append(SearchResult(res['title'], res['url'], snippet=res['content']))
            else:
                result_objs.append(SearchResult(res['title'], res['url'], snippet=res['content']))
        return result_objs, None


PROVIDER_TO_WEB = {
    'bing': Bing,
    'searxng': SearXNG,
}

def make_code_from_setting(eng):
    engine = eng['engine'] if 'engine' in eng else None
    provider = eng['provider']
    return eng['code'] if 'code' in eng else (f"{engine}-{provider}" if engine else provider)

"""
Settings look like:

web:
  engines:
    - provider: searxng  # required
        engine: "google"  # optional
        name: "Google"  # optional
        desc: "One of the best search engines ever!"  # optional
        traits: "General"  # optional

"""
def generate_engines():
    if 'web' not in SETTINGS:
        return {}
    if 'engines' not in SETTINGS['web'] or not len(SETTINGS['web']['engines']):
        return {}
    
    to_return = {}
    options = SETTINGS['web']['engines']
    for option in options:
        if 'disabled' in option and option['disabled']:
            continue
        provider = option['provider']
        provider_class = PROVIDER_TO_WEB[provider]
        engine = option['engine'] if 'engine' in option else None
        code = make_code_from_setting(option)
        name = option['name'] if 'name' in option else (engine if engine else provider)
        traits = option['traits'] if 'traits' in option else ""
        desc = option['desc'] if 'desc' in option else (f"The search engine {engine} is provided by {provider}." if engine else "")
        use_pdf = option['use_pdf'] if 'use_pdf' in option else False
        market = option['market'] if 'market' in option else None
        obj = provider_class(
            engine=engine,
            code=code,
            name=name,
            desc=desc,
            traits=traits,
            use_pdf=use_pdf,
            market=market
        )
        to_return[code] = obj
    return to_return


SEARCH_PROVIDERS = generate_engines()

def generate_default():
    if 'web' not in SETTINGS:
        return ""
    if 'engines' not in SETTINGS['web'] or not len(SETTINGS['web']['engines']):
        return ""

    engines = SETTINGS['web']['engines']

    if 'default' in SETTINGS['web']:
        default = SETTINGS['web']['default']
        if default not in SEARCH_PROVIDERS:
            print(f"\n\nWARNING: a default you specified, '{default}', does not exist. Make sure you're using the correct code schema as specified in the README. Instead, '{make_code_from_setting(engines[0])}' will be used as the default.\n\n", file=sys.stderr)
        else:
            return SETTINGS['web']['default']

    return make_code_from_setting(engines[0])  # first available 

DEFAULT_SEARCH_ENGINE = generate_default()
