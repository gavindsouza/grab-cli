import shutil
import sys
from html.parser import HTMLParser
from http.client import RemoteDisconnected
from multiprocessing import Pool, cpu_count
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class Site:
    def __init__(self, url: str) -> None:
        self.location = urlparse(url)

    @property
    def url(self) -> str:
        return self.location.geturl()


class Scraper:
    def __init__(self, target: Site) -> None:
        self.target = target
        self.request_count = 0

    def fetch(self, url: str):
        self.last_response = urlopen(
            Request(url=url, headers={"User-Agent": "Mozilla/5.0"})
        )
        self.request_count += 1

    @property
    def feed(self):
        return self.last_response.read().decode("utf-8")


class HyperlinkParser(HTMLParser):
    def __init__(
        self,
        *args,
        accepted_extns,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._filtered_links = []
        self.accepted_extns = accepted_extns

    @property
    def filtered_links(self) -> list:
        return list(set(self._filtered_links))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href" and any(
                    attr[1] for pattern in self.accepted_extns if pattern in attr[1]
                ):
                    self._filtered_links.append(attr[1])


def resilient_request(url: str, retries: int = 3):
    for _ in range(retries):
        try:
            return urlopen(url)
        except RemoteDisconnected:
            continue
    raise RemoteDisconnected


def download_file(target: str, path: str):
    print(f"Downloading {target} to {path}")
    with resilient_request(target) as response, open(path, "wb") as out_file:
        shutil.copyfileobj(response, out_file)


def bulk_download(urls: list[str], download_location: str, metadata=None):
    location = Path(download_location)
    location.mkdir(parents=True, exist_ok=True)
    (location / "metadata.txt").write_text(
        f"{metadata or ''}\n\nURLS Found:\n" + "\n".join(urls)
    )

    cpu_pool = Pool(processes=cpu_count())
    job_kwargs = [(url, location / url.rsplit("/", 1)[-1]) for url in urls]

    cpu_pool.starmap(download_file, job_kwargs)


if __name__ == "__main__":
    url = sys.argv[1]
    pull_type = sys.argv[2]


    extns = {
        "videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    }

    if pull_type == "*":
        extns = [extn for extn_list in extns.values() for extn in extn_list]
    else:
        extns = extns[pull_type]

    target = Site(url)
    scraper = Scraper(target)
    scraper.fetch(scraper.target.url)

    parser = HyperlinkParser(accepted_extns=extns)
    parser.feed(scraper.feed)

    target_folder = "_".join(url.rsplit("/", 2)[-2:])
    files_to_download = [f"{target.location.scheme}:{x}" for x in parser.filtered_links]

    bulk_download(
        urls=files_to_download,
        download_location=target_folder,
        metadata=f"Scraped all {extns} files from {url}",
    )
