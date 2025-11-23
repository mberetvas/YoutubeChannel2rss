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

__version__ = "1.0.0"

import re
import argparse
import json
import csv
import sys
import time
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup, FeatureNotFound, ResultSet, PageElement, Tag, NavigableString
import pyperclip


def get_cache_file_path() -> Path:
    """
    Get the path to the cache file for storing channel ID mappings.

    Returns:
        Path: The path to the cache file.
    """
    cache_dir = Path.home() / ".youtuberss"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / "cache.json"


def load_cache() -> dict:
    """
    Load the cache from the cache file.

    Returns:
        dict: The cached channel ID mappings.
    """
    cache_file = get_cache_file_path()
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_cache(cache: dict) -> None:
    """
    Save the cache to the cache file.

    Args:
        cache (dict): The cache to save.
    """
    cache_file = get_cache_file_path()
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except IOError as e:
        print(f"Warning: Could not save cache: {e}")


def get_cached_channel_id(url: str, use_cache: bool = True) -> str | None:
    """
    Get a cached channel ID for a URL if available.

    Args:
        url (str): The YouTube URL.
        use_cache (bool): Whether to use the cache.

    Returns:
        str | None: The cached channel ID if available, None otherwise.
    """
    if not use_cache:
        return None
    
    cache = load_cache()
    cache_entry = cache.get(url)
    if cache_entry:
        # Check if cache entry has timestamp and channel_id
        if isinstance(cache_entry, dict) and "channel_id" in cache_entry:
            return cache_entry["channel_id"]
        # Legacy cache format (just the channel ID as a string)
        return cache_entry
    return None


def cache_channel_id(url: str, channel_id: str) -> None:
    """
    Cache a channel ID for a URL.

    Args:
        url (str): The YouTube URL.
        channel_id (str): The channel ID.
    """
    cache = load_cache()
    cache[url] = {
        "channel_id": channel_id,
        "timestamp": datetime.now().isoformat()
    }
    save_cache(cache)


def clear_cache() -> None:
    """
    Clear the cache file.
    """
    cache_file = get_cache_file_path()
    if cache_file.exists():
        cache_file.unlink()
        print(f"Cache cleared: {cache_file}")
    else:
        print("No cache file to clear.")


def retry_request(func, *args, max_retries=3, backoff_factor=2, **kwargs):
    """
    Retry a function with exponential backoff.

    Args:
        func: The function to retry.
        max_retries: Maximum number of retry attempts (default: 3).
        backoff_factor: Multiplier for exponential backoff (default: 2).
        *args, **kwargs: Arguments to pass to the function.

    Returns:
        The result of the function if successful, None otherwise.
    """
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            return result
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                print(f"Timeout. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                wait_time = backoff_factor ** attempt
                print(f"Connection error. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise
    return None


def get_youtube_source_code(url: str) -> bytes | None:
    """
    Fetches the source code of a YouTube page.

    Args:
        url (str): The URL of the YouTube page.

    Returns:
        bytes: The content of the YouTube page if the request is successful.
        None: If there is an error fetching the URL.
    """
    def _fetch():
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    
    try:
        return retry_request(_fetch)
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out while fetching URL: {url}")
        print("Suggestion: Check your internet connection or try again later.")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Error: YouTube page not found (404): {url}")
            print("Suggestion: Verify the URL is correct and the channel exists.")
        else:
            print(f"Error: HTTP error {e.response.status_code} while fetching URL: {url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Error: Connection error while fetching URL: {url}")
        print("Suggestion: Check your internet connection.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        print("Suggestion: Check the URL format and try again.")
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
        # Support both /channel/ and /@handle URLs
        match = re.search(r"/channel/([UC][a-zA-Z0-9_-]+)", og_url)
        if match:
            return match.group(1)
        # Check if this is a handle URL - the channel ID might be elsewhere
        handle_match = re.search(r"/@([a-zA-Z0-9_-]+)", og_url)
        if handle_match:
            # Continue to other methods to find the actual channel ID
            pass

    # Method 2: Script tags (fallback)
    script_tags = soup.find_all("script")
    for script in script_tags:
        script_content = str(script)
        match = re.search(r"\"channel_id\":\"([UC][a-zA-Z0-9_-]+)\"", script_content)
        if match:
            return match.group(1)
        # Also look for channelId pattern
        match = re.search(r"\"channelId\":\"([UC][a-zA-Z0-9_-]+)\"", script_content)
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
    def _fetch():
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        return response.content
    
    try:
        content = retry_request(_fetch)
        if content is None:
            return None
        try:
            soup = BeautifulSoup(content, "xml")
        except FeatureNotFound:
            print(
                "Error: Couldn't find a tree builder with the features you requested: xml."
                " Please install the 'lxml' parser library using 'pip install lxml'."
            )
            return None
        _entries = soup.find_all("entry")[:limit]
        return _entries
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out while fetching RSS feed: {feed_url}")
        print("Suggestion: Check your internet connection or try again later.")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Error: RSS feed not found (404): {feed_url}")
            print("Suggestion: The channel might not have any videos or the feed is unavailable.")
        elif e.response.status_code == 429:
            print(f"Error: Rate limited (429) while fetching RSS feed: {feed_url}")
            print("Suggestion: You're making too many requests. Wait a while before trying again.")
        else:
            print(f"Error: HTTP error {e.response.status_code} while fetching RSS feed: {feed_url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return None


def filter_videos(
    param_entries: list[BeautifulSoup],
    filter_by: str | None = None,
    filter_value: str | None = None,
    after_date: str | None = None,
    before_date: str | None = None,
) -> list[dict[str, str]]:
    """
    Filters videos by date, title, or other metadata.
    Multiple filters are combined using AND logic.

    Args:
        param_entries (list): A list of BeautifulSoup 'entry' elements representing the videos.
        filter_by (str, optional): The criteria to filter videos by ('date' or 'title').
        filter_value (str, optional): The value to filter videos by. Defaults to None.
        after_date (str, optional): Filter videos published after this date (YYYY-MM-DD).
        before_date (str, optional): Filter videos published before this date (YYYY-MM-DD).

    Returns:
        list: A list of dictionaries containing filtered video details.
    """
    filtered_videos = []
    
    # Parse date range if provided
    after_dt = datetime.strptime(after_date, "%Y-%m-%d").date() if after_date else None
    before_dt = datetime.strptime(before_date, "%Y-%m-%d").date() if before_date else None
    
    for entry in param_entries:
        title = entry.find("title").text
        published = entry.find("published").text
        link = entry.find("link")["href"]
        entry_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%S%z")
        
        # Apply date range filters (AND logic)
        if after_dt and entry_date.date() < after_dt:
            continue
        if before_dt and entry_date.date() > before_dt:
            continue

        # Apply legacy date filter (exact match)
        if filter_by == "date":
            filter_date = datetime.strptime(filter_value, "%Y-%m-%d")
            if entry_date.date() != filter_date.date():
                continue
        
        # Apply title filter (AND logic with date filters)
        if filter_by == "title":
            if filter_value.lower() not in title.lower():
                continue
        
        # If we made it here, the video passed all filters
        filtered_videos.append({"title": title, "published": published, "link": link})
    
    return filtered_videos


def format_output(videos: list[dict[str, str]], output_format: str = "text") -> None:
    """
    Format and display videos in the specified output format.

    Args:
        videos (list): A list of dictionaries containing video details.
        output_format (str): The output format ('text', 'json', or 'csv').
    """
    if output_format == "json":
        print(json.dumps(videos, indent=2))
    elif output_format == "csv":
        if videos:
            writer = csv.DictWriter(sys.stdout, fieldnames=["title", "published", "link"])
            writer.writeheader()
            writer.writerows(videos)
    else:  # text format (default)
        for video in videos:
            print(f"Title: {video['title']}")
            print(f"Published: {video['published']}")
            print(f"Link: {video['link']}\n")


if __name__ == "__main__":
    # Initialize argument parser with description and example usage
    parser = argparse.ArgumentParser(
        description="Convert YouTube channel URL to RSS feed URL and fetch latest videos.",
        epilog="Example usage: "
        "python main.py https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw"
        " --filter_by date --filter_value 2023-10-01",
    )

    # Add version argument
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program version and exit",
    )

    # Add argument for YouTube channel URL (made optional if --channel-id is provided)
    parser.add_argument(
        "youtube_url", 
        nargs="?",
        help="The YouTube channel URL (e.g., https://www.youtube.com/@username or "
             "https://www.youtube.com/channel/UC...)"
    )

    # Add optional argument for filtering videos by date or title
    parser.add_argument(
        "--filter_by", choices=["date", "title"], help="Filter videos by date or title"
    )

    # Add optional argument for the value to filter videos by
    parser.add_argument(
        "--filter_value",
        help="Value to filter videos by (e.g., date in YYYY-MM-DD format or title keyword)",
    )

    # Add optional argument for configurable video limit
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum number of videos to fetch (default: 5)",
    )

    # Add optional argument for quiet mode
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress informational messages (only show errors and video information)",
    )

    # Add optional argument to save RSS URL to file
    parser.add_argument(
        "--save-url",
        metavar="FILENAME",
        help="Save RSS feed URL to specified file instead of clipboard",
    )

    # Add optional argument for output format
    parser.add_argument(
        "--output",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format for video list (default: text)",
    )

    # Add optional arguments for date range filtering
    parser.add_argument(
        "--after",
        metavar="DATE",
        help="Filter videos published after this date (YYYY-MM-DD format)",
    )
    parser.add_argument(
        "--before",
        metavar="DATE",
        help="Filter videos published before this date (YYYY-MM-DD format)",
    )

    # Add optional argument for direct channel ID
    parser.add_argument(
        "--channel-id",
        metavar="ID",
        help="Directly provide the YouTube channel ID (skips URL parsing)",
    )

    # Add optional argument for dry run mode
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fetched without actually fetching RSS feed",
    )

    # Add optional argument to disable cache
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable channel ID caching",
    )

    # Add optional argument to clear cache
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the channel ID cache and exit",
    )

    # Parse command-line arguments
    args = parser.parse_args()

    # Handle cache clearing
    if args.clear_cache:
        clear_cache()
        sys.exit(0)

    # Validate that either youtube_url or --channel-id is provided
    if not args.youtube_url and not args.channel_id:
        parser.error("Either youtube_url or --channel-id must be provided")

    # Extract YouTube URL from parsed arguments
    youtube_url = args.youtube_url
    quiet_mode = args.quiet

    # Determine channel ID
    channel_id = None
    if args.channel_id:
        # Use directly provided channel ID
        channel_id = args.channel_id
        if not quiet_mode:
            print(f"Using provided channel ID: {channel_id}")
    else:
        # Check cache first
        use_cache = not args.no_cache
        channel_id = get_cached_channel_id(youtube_url, use_cache)
        
        if channel_id:
            if not quiet_mode:
                print(f"Using cached channel ID: {channel_id}")
        else:
            # Fetch the source code of the YouTube page
            source_code = get_youtube_source_code(youtube_url)
            if source_code:
                # Extract the channel ID from the source code
                channel_id = get_youtube_channel_id(source_code)
                # Cache the channel ID for future use
                if channel_id and use_cache:
                    cache_channel_id(youtube_url, channel_id)
            else:
                print("Error: Could not fetch YouTube page content.")
                print("Suggestion: Check the URL format (e.g., https://www.youtube.com/channel/CHANNEL_ID)")
                sys.exit(1)

    if channel_id:
        # Create the RSS feed URL using the channel ID
        rss_feed_url = create_rss_feed_url(channel_id)
        if rss_feed_url:
            if not quiet_mode:
                print(f"Channel ID: {channel_id}")
                print(f"RSS Feed URL: {rss_feed_url}")
            
            # Dry run mode - show what would be fetched and exit
            if args.dry_run:
                print("\n--- DRY RUN MODE ---")
                print(f"Would fetch up to {args.limit} videos from RSS feed")
                if args.filter_by:
                    print(f"Would filter by {args.filter_by}: {args.filter_value}")
                if args.after:
                    print(f"Would filter videos after: {args.after}")
                if args.before:
                    print(f"Would filter videos before: {args.before}")
                if args.output != "text":
                    print(f"Would output in {args.output} format")
                if args.save_url:
                    print(f"Would save RSS URL to: {args.save_url}")
                else:
                    print("Would copy RSS URL to clipboard")
                print("--- END DRY RUN ---")
                sys.exit(0)
            
            # Save URL to file or clipboard
            if args.save_url:
                try:
                    with open(args.save_url, "w", encoding="utf-8") as f:
                        f.write(rss_feed_url)
                    if not quiet_mode:
                        print(f"RSS feed URL has been saved to {args.save_url}")
                except IOError as e:
                    print(f"Error saving URL to file: {e}")
            else:
                pyperclip.copy(rss_feed_url)  # Copy RSS feed URL to clipboard
                if not quiet_mode:
                    print("RSS feed URL has been copied to the clipboard.")

            # Fetch and parse the RSS feed content
            entries = fetch_rss_feed_content(rss_feed_url, limit=args.limit)
            if entries:
                # Filter videos based on provided criteria
                videos = filter_videos(
                    entries, 
                    args.filter_by, 
                    args.filter_value,
                    args.after,
                    args.before
                )
                # Format and display videos
                format_output(videos, args.output)
            else:
                print("Could not fetch RSS feed content.")
        else:
            print("Error: Could not create RSS feed URL from channel ID.")
    else:
        print("Error: Channel ID not found in the YouTube page.")
        print("Suggestion: The URL might be invalid or the page structure has changed.")
