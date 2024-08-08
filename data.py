# Class representing the data from the page source
from bs4 import BeautifulSoup


class Data:
    def __init__(self, type, page_source):
        self.type = type
        soup = BeautifulSoup(page_source, "html.parser")
        if type == "archive":
            self.data = soup.find("table", "directory-listing-table")
        else:
            self.data = soup.find("pre")
            self.type = "pre"
            if self.data is None:
                self.data = soup.find("body")
                self.type = "body"

    def __iter__(self):
        if self.type == "archive":
            for i, tr in enumerate(self.data.find_all("tr")):
                if i <= 1:
                    continue
                link = tr.find("a")
                yield link.get("href")
        elif self.type == "pre" or self.type == "body":
            for i, a in enumerate(self.data.find_all("a")):
                yield a.get("href")