import sys
from grab_cli.hound import Site, Scraper, HyperlinkParser, bulk_download
from grab_cli.utils import build_url, show_help, track_exec_time


def execute_via_cli():
    help_asked = "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) < 3
    if help_asked:
        return show_help()
    verbose = "-v" in sys.argv
    if verbose:
        sys.argv.remove("-v")
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
    parser = HyperlinkParser(accepted_extns=extns)

    with track_exec_time(show=verbose, verb="Request"):
        scraper.fetch(scraper.target.url)

    with track_exec_time(show=verbose, verb="Parsing"):
        parser.feed(scraper.feed)

    target_folder = "_".join(url.rsplit("/", 2)[-2:])
    files_to_download = [
        build_url(x, scheme=target.location.scheme) for x in parser.filtered_links
    ]

    with track_exec_time(show=verbose, verb="Downloading"):
        bulk_download(
            urls=files_to_download,
            download_location=target_folder,
            metadata=f"Scraped all {extns} files from {url}",
        )


if __name__ == "__main__":
    execute_via_cli()
