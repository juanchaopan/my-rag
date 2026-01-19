from requests import get
from bs4 import BeautifulSoup


def download_pdf():
    url = "https://docs.oracle.com/en/applications/jd-edwards/asset-lifecycle/9.2/guides.html"
    response = get(url)
    content = response.content
    soup = BeautifulSoup(content, "html.parser")
    anchors = soup.find_all("a", class_="pdf-book-link")
    pass


if __name__ == "__main__":
    download_pdf()
