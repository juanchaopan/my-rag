from bs4 import BeautifulSoup
from scrapy import Request, Spider
from langchain_ai_docs.items import LangchainAiDocsItem
from langchain_ai_docs.settings import LANGCHAIN_AI_DOCS_URL, OLLAMA_URL
from urllib.parse import urlparse
from markdownify import markdownify
from readability import Document
from requests import get
from base64 import b64decode, b64encode
from ollama import Client
from cairosvg import svg2png
from magika import Magika


class DocsSpider(Spider):
    name = "docs_spider"
    start_urls = [LANGCHAIN_AI_DOCS_URL]
    allowed_domains = [urlparse(LANGCHAIN_AI_DOCS_URL).hostname]
    magika = Magika()
    client = Client(host=OLLAMA_URL)

    def parse(self, response):
        text = response.text
        soup = BeautifulSoup(text, "html.parser")

        hrefs = [x.get("href") for x in soup.find_all("a")]
        for href in [x for x in hrefs if urlparse(x).scheme == ""]:
            yield Request(url=response.urljoin(href), callback=self.parse)

        content = str(soup.select_one("div#content-area"))
        content_soup = BeautifulSoup(content, "html.parser")

        for img in content_soup.find_all("img"):
            description = self.get_description(response.urljoin(img.get("src", "")))
            if description:
                img["alt"] = description

        clean_content = Document(str(content_soup)).content()
        markdown = markdownify(clean_content)

        yield LangchainAiDocsItem(id=urlparse(response.url).path, content=markdown)

    def get_description(self, image_src: str) -> str | None:
        try:
            if image_src.startswith("data:"):
                _, b64 = image_src.split(",", 1)
                content = b64decode(b64)
            else:
                response = get(image_src)
                output = self.magika.identify_bytes(response.content).output
                match output.label:
                    case "svg":
                        content = svg2png(bytestring=response.content)
                    case "bmp" | "gif" | "jpeg" | "png" | "webp":
                        content = response.content
                    case _:
                        raise ValueError(
                            f"Image content is {output.label}, description unavailable."
                        )
            encoded_image = b64encode(content).decode("utf-8")
            response = self.client.chat(
                model="moondream:1.8b",
                messages=[
                    {
                        "role": "user",
                        "content": "Describe this image in detail, including what elements are shown, what information it presents, and what concept it conveys.",
                        "images": [encoded_image],
                    }
                ],
                stream=False,
            )
            return response.message.content.strip()
        except ValueError as ve:
            return None
