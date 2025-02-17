"""
Script converts a YouTube channel URL to RSS feed URL and fetches latest videos from the RSS feed.
It allows filtering videos by date or title.

Modules:
    requests: To make HTTP requests to fetch YouTube page source code and RSS feed content.
    bs4 (BeautifulSoup): To parse HTML and XML content.
    re: To perform regular expression matching.
    argparse: To handle command-line arguments.
    datetime: To handle date and time operations.
    pyperclip: To copy the RSS feed URL to the clipboard.

Functions:
    get_youtube_source_code(youtube_url): Fetches the source code of a YouTube page.
    get_youtube_channel_id(source_code): Extracts the channel ID from the YouTube source code.
    create_rss_feed_url(channel_id): Creates the RSS feed URL from the channel ID.
    fetch_rss_feed_content(rss_feed_url, limit=5): Fetches and parses the RSS feed content.
    filter_videos(entries, filter_by=None, filter_value=None): Filters videos.

Usage:
    python main.py <youtube_url> [--filter_by <filter_by>] [--filter_value <filter_value>]

Example:
    python
    main.py
    https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw
    --filter_by date
    --filter_value 2023-10-01
"""

import re
import argparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup, FeatureNotFound, ResultSet, PageElement, Tag, NavigableString
import pyperclip


def get_youtube_source_code(url: str) -> bytes | None:
    """
    Fetches the source code of a YouTube page.

    Args:
        url (str): The URL of the YouTube page.

    Returns:
        bytes: The content of the YouTube page if the request is successful.
        None: If there is an error fetching the URL.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for bad status codes
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None


def get_youtube_channel_id(html_source_code: bytes | None) -> str | None:
    """
    Extracts the channel ID from the YouTube source code.

    Args:
        html_source_code (bytes): The HTML source code of the YouTube page.

    Returns:
        str: The channel ID if found, otherwise None.
    """
    if html_source_code is None:
        return None

    soup = BeautifulSoup(html_source_code, "html.parser")

    # Method 1: Meta tag (most reliable)
    meta_tag = soup.find("meta", property="og:url")
    if meta_tag:
        og_url = meta_tag.get("content")
        match = re.search(r"/channel/([UC][a-zA-Z0-9_-]+)", og_url)
        if match:
            return match.group(1)

    # Method 2: Script tags (fallback)
    script_tags = soup.find_all("script")
    for script in script_tags:
        script_content = str(script)
        match = re.search(r"\"channel_id\":\"([UC][a-zA-Z0-9_-]+)\"", script_content)
        if match:
            return match.group(1)

    return None


def create_rss_feed_url(cid: str) -> str | None:
    """
    Creates the RSS feed URL from the YouTube channel ID.

    Args:
        cid (str): The YouTube channel ID.

    Returns:
        str: The RSS feed URL if the channel ID is provided, otherwise None.
    """
    if cid:
        return f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
    return None


def fetch_rss_feed_content(
    feed_url: str, limit: int = 5
) -> ResultSet[PageElement | Tag | NavigableString] | None:
    """
    Fetches and parses the RSS feed content, limited to the latest videos.

    Args:
        feed_url (str): The URL of the RSS feed.
        limit (int, optional): The maximum number of videos to fetch. Defaults to 5.

    Returns:
        list: A list of BeautifulSoup 'entry' elements representing the videos if successful.
        None: If there is an error fetching the RSS feed or parsing the content.
    """
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        try:
            soup = BeautifulSoup(response.content, "xml")
        except FeatureNotFound:
            print(
                "Error: Couldn't find a tree builder with the features you requested: xml."
                " Please install the 'lxml' parser library using 'pip install lxml'."
            )
            return None
        _entries = soup.find_all("entry")[:limit]
        return _entries
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return None


def filter_videos(
    param_entries: list[BeautifulSoup],
    filter_by: str | None = None,
    filter_value: str | None = None,
) -> list[dict[str, str]]:
    """
    Filters videos by date, title, or other metadata.

    Args:
        param_entries (list): A list of BeautifulSoup 'entry' elements representing the videos.
        filter_by (str, optional): The criteria to filter videos by ('date' or 'title').
        filter_value (str, optional): The value to filter videos by. Defaults to None.

    Returns:
        list: A list of dictionaries containing filtered video details.
    """
    filtered_videos = []
    for entry in param_entries:
        title = entry.find("title").text
        published = entry.find("published").text
        link = entry.find("link")["href"]

        if filter_by == "date":
            entry_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%S%z")
            filter_date = datetime.strptime(filter_value, "%Y-%m-%d")
            if entry_date.date() == filter_date.date():
                filtered_videos.append({"title": title, "published": published, "link": link})
        elif filter_by == "title" and filter_value.lower() in title.lower():
            filtered_videos.append({"title": title, "published": published, "link": link})
        elif not filter_by:
            filtered_videos.append({"title": title, "published": published, "link": link})
    return filtered_videos


if __name__ == "__main__":
    # Initialize argument parser with description and example usage
    parser = argparse.ArgumentParser(
        description="Convert YouTube channel URL to RSS feed URL and fetch latest videos.",
        epilog="Example usage: "
        "python main.py https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw"
        " --filter_by date --filter_value 2023-10-01",
    )

    # Add argument for YouTube channel URL
    parser.add_argument("youtube_url", help="The YouTube channel URL")

    # Add optional argument for filtering videos by date or title
    parser.add_argument(
        "--filter_by", choices=["date", "title"], help="Filter videos by date or title"
    )

    # Add optional argument for the value to filter videos by
    parser.add_argument(
        "--filter_value",
        help="Value to filter videos by (e.g., date in YYYY-MM-DD format or title keyword)",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Extract YouTube URL from parsed arguments
    youtube_url = args.youtube_url

    # Fetch the source code of the YouTube page
    source_code = get_youtube_source_code(youtube_url)
    if source_code:
        # Extract the channel ID from the source code
        channel_id = get_youtube_channel_id(source_code)
        if channel_id:
            # Create the RSS feed URL using the channel ID
            rss_feed_url = create_rss_feed_url(channel_id)
            if rss_feed_url:
                print(f"Channel ID: {channel_id}")
                print(f"RSS Feed URL: {rss_feed_url}")
                pyperclip.copy(rss_feed_url)  # Copy RSS feed URL to clipboard
                print("RSS feed URL has been copied to the clipboard.")

                # Fetch and parse the RSS feed content
                entries = fetch_rss_feed_content(rss_feed_url)
                if entries:
                    # Filter videos based on provided criteria
                    videos = filter_videos(entries, args.filter_by, args.filter_value)
                    for video in videos:
                        print(f"Title: {video['title']}")
                        print(f"Published: {video['published']}")
                        print(f"Link: {video['link']}\n")
                else:
                    print("Could not fetch RSS feed content.")
            else:
                print("Could not create RSS feed URL.")
        else:
            print("Channel ID not found.")
