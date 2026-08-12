#!/usr/bin/env python -B
# vi: set syntax=python ts=4 sw=4 sts=4 et ff=unix ai si :
#
# (c) Steven Scholnick <scholnicks@gmail.com>
# The lyricsipsum source code is published under a MIT license.

"""
lyricsipsum: Generates Lorem Ipsum text using a download song's lyrics

Usage:
    lyricsipsum [options]

Options:
    -c, --clean         Remove profanity from returned lyrics
    -d, --debug         Debug mode
    -h, --help          Show this help screen
    -m, --max=<num>     Maximum number characters for the returned lyrics
    -n, --number=<num>  Number of songs to download [default: 50]
    -s, --save=<artist> Save lyrics for <artist>
    -t, --title         Print the song title along with the lyrics
    --version           Prints the version
"""

import json
import os
import random
import re
import sys
import tomllib
from dataclasses import asdict, dataclass
from importlib.metadata import version
from pathlib import Path

from better_profanity import profanity
from docopt import docopt
from lyricsgenius import Genius

arguments = {}


@dataclass(frozen=True)
class Song:
    artist: str
    title: str
    lyrics: str


def main() -> None:
    """Main Method"""
    global arguments
    arguments = docopt(__doc__, version=f"lyricsipsum {version('lyricsipsum')}")

    if not configDirectory().exists():
        configDirectory().mkdir(parents=True, exist_ok=True)

    if arguments["--save"]:
        saveLyricsToFile()
    else:
        song = random.choice(readLyricsFromFile())
        lyrics = (profanity.censor(song.lyrics) if arguments["--clean"] else song.lyrics).strip()
        if arguments["--title"]:
            print(f"{song.title}\n", file=sys.stderr)

        if arguments["--max"]:
            print(lyrics[0 : int(arguments["--max"])])
        else:
            print(lyrics)

    sys.exit(0)


def readLyricsFromFile() -> list[Song]:
    """Reads lyrics from a file and returns a list of Song objects"""
    try:
        with jsonPath().open("r") as f:
            return [Song(**song) for song in json.load(f)]
    except FileNotFoundError:
        print(f"No lyrics file found at {jsonPath()}. Run with --save to create one.", file=sys.stderr)
        sys.exit(1)


def saveLyricsToFile() -> None:
    """Fetches lyrics from Genius and saves them to a file"""
    songs = set(readLyricsFromFile()) if jsonPath().exists() else set()
    count = len(songs)

    artist = buildGenius().search_artist(arguments["--save"], max_songs=int(arguments["--number"]), sort="popularity")
    if artist is None:
        print(f'Artist "{arguments["--save"]}" not found.', file=sys.stderr)
        sys.exit(1)

    for song in artist.songs:
        if song.lyrics:
            if arguments["--debug"]:
                print(f"Adding {song.title}", file=sys.stderr)
            songs.add(
                Song(
                    artist=arguments["--save"],
                    title=song.title,
                    lyrics=re.sub(r"\n+", "\n", song.lyrics).strip('"').strip(),
                )
            )

    with jsonPath().open("w") as f:
        json.dump(
            [asdict(s) for s in sorted(songs, key=lambda s: (s.artist.lower(), s.title.lower()))],
            f,
            indent=4,
        )

    print(f"Added {len(songs) - count} songs to {jsonPath()}")


def jsonPath() -> Path:
    """Returns the path to the JSON file containing lyrics"""
    return configDirectory() / "songs.json"


def buildGenius() -> Genius:
    """Builds and returns a Genius object"""

    if os.environ.get("GENIUS_ACCESS_TOKEN", "").strip() == "":
        print("GENIUS_ACCESS_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    config = {}
    configFile = configDirectory() / "config.toml"
    if configFile.exists():
        with configFile.open("rb") as f:
            config = tomllib.load(f)

    genius = Genius(os.environ.get("GENIUS_ACCESS_TOKEN"))
    genius.verbose = arguments["--debug"] or config.get("client", {}).get("verbose", False)
    genius.skip_non_songs = config.get("client", {}).get("skip_non_songs", True)
    genius.excluded_terms = config.get("client", {}).get("excluded_terms", ["(Remix)", "(Live)"])
    genius.remove_section_headers = config.get("client", {}).get("remove_section_headers", True)
    genius.timeout = int(config.get("client", {}).get("timeout", 15))

    if arguments["--debug"]:
        print(
            f"Genius: Verbose:{genius.verbose}, exclude:{genius.excluded_terms}, timeout:{genius.timeout}",
            file=sys.stderr,
        )

    return genius


def configDirectory() -> Path:
    """Returns the path to the configuration directory"""
    return Path.home() / ".config" / "lyricsipsum"


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
