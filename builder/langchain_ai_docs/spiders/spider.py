from bs4 import BeautifulSoup
from scrapy import Request, Spider
from trafilatura import extract
from langchain_ai_docs.items import LangchainAiDocsItem
from langchain_ai_docs.settings import LANGCHAIN_AI_DOCS_URL
from urllib.parse import urlparse


class DocsSpider(Spider):
    name = "docs_spider"
    start_urls = [LANGCHAIN_AI_DOCS_URL]
    allowed_domains = [urlparse(LANGCHAIN_AI_DOCS_URL).hostname]

    def parse(self, response):
        text = response.text
        soup = BeautifulSoup(text, "html.parser")
        hrefs = [x.get("href") for x in soup.find_all("a")]
        for href in [x for x in hrefs if urlparse(x).scheme == ""]:
            yield Request(url=response.urljoin(href), callback=self.parse)
        yield LangchainAiDocsItem(id=urlparse(response.url).path, content=extract(text))
