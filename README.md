# lyricsipsum

lyricsipsum randomly selects a downloaded song's lyrics as a replacement for standard boring lorem ipsum text.

```
Usage:
    lyricsipsum [options]

Options:
    -c, --clean         Remove profanity from return lyrics
    -d, --debug         Debug mode
    -h, --help          Show this help screen
    -n, --number=<num>  Number of songs to download [default: 50]
    -s, --save=<artist> Save lyrics for <artist>
    -t, --title         Print the song title along with the lyrics
    --version           Prints the version
```

## Installation

```bash
pipx install lyricsipsum
```

### Create Configuration Directory
```bash
mkdir -p ~/.config/lyricsipsum
```

### Create configuration file
```bash
cat <<EOF > ~/.config/lyricsipsum.config.toml
[client]
verbose=true
skip_non_song=true
excluded_terms=["(Remix)", "(Live)", "(Explicit)"]
remove_section_headers=true
timeout=15
EOF
```

### Setup Genuis API Access
Following Authorization instructions on https://lyricsgenius.readthedocs.io/en/master/setup.html

## License
lyricsipsum is freeware released under the [MIT License](https://github.com/scholnicks/lyricsipsum/blob/main/LICENSE).
