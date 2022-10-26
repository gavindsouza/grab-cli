# grab-cli

Light-weight web scraper to download specific types of media from static sites

## Installation

Use `pipx` to try out grab!

```bash
pipx install git+https://github.com/gavindsouza/grab-cli.git
```

## Usage

```bash
grab <url-of-static-page> 'images' # download all images from url 
grab <url-of-static-page> 'videos' # downlaod all videos
grab <url-of-static-page> '*' # download all images and videos
```

## How it works

Upon running `grab https://www.reddit.com/r/meme/comments/ye14vl/cable_with_extra_steps_src_unknown/ images`, you'd get the meme neatly dumped under *cable_with_extra_steps_src_unknown_/dn5m80fv66w91.png*.
