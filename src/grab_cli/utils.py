from contextlib import contextmanager


def show_help():
    print("Usage: grab <url> <type>")
    print("Type can be one of: videos, images, *")


@contextmanager
def track_exec_time(show: bool = False, verb: str = None):
    if show:
        from time import monotonic

        start = monotonic()
    yield
    if show:
        verb = verb or "Execution"
        print(f"{verb} took {monotonic() - start:.02} seconds")


def build_url(origin: str, scheme: str) -> str:
    if origin.startswith("//"):
        return f"{scheme}:{origin}"
    if scheme not in origin:
        return f"{scheme}://{origin}"
    return origin
