from unittest.mock import patch
from bs4 import BeautifulSoup
import requests

from main import (
    get_youtube_source_code,
    get_youtube_channel_id,
    create_rss_feed_url,
    fetch_rss_feed_content,
    filter_videos,
)


def test_get_youtube_source_code_success():
    """
    Test case for successfully retrieving YouTube source code.

    This test mocks the `requests.get` method to simulate a successful HTTP GET request
    to a YouTube channel URL. It verifies that the `get_youtube_source_code` function
    returns the expected HTML content when the request is successful.

    Steps:
    1. Define the YouTube channel URL.
    2. Define the expected HTML content to be returned by the mocked request.
    3. Mock the `requests.get` method to return a successful response with the expected content.
    4. Call the `get_youtube_source_code` function with the URL.
    5. Assert that the returned content matches the expected content.
    """
    url = "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw"
    expected_content = b"<html>Mocked YouTube Page</html>"

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = expected_content

        result = get_youtube_source_code(url)
        assert result == expected_content


def test_get_youtube_source_code_failure():
    """
    Test case for handling failure when retrieving YouTube source code.

    This test mocks the `requests.get` method to simulate a failed HTTP GET request
    to a YouTube channel URL. It verifies that the `get_youtube_source_code` function
    returns None when the request fails.

    Steps:
    1. Define the YouTube channel URL.
    2. Mock the `requests.get` method to raise a `requests.exceptions.RequestException`.
    3. Call the `get_youtube_source_code` function with the URL.
    4. Assert that the returned result is None.
    """
    url = "https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw"

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Mocked Exception")

        result = get_youtube_source_code(url)
        assert result is None


def test_get_youtube_channel_id_meta_tag():
        """
        Test case for extracting YouTube channel ID from a meta tag.

        This test verifies that the `get_youtube_channel_id` function correctly extracts
        the channel ID from the 'og:url' meta tag in the provided HTML source code.

        Steps:
        1. Define the HTML source code containing the 'og:url' meta tag with the channel ID.
        2. Call the `get_youtube_channel_id` function with the HTML source code.
        3. Assert that the extracted channel ID matches the expected channel ID.
        """
        html_source_code = b'<meta property="og:url" content="https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw">'
        result = get_youtube_channel_id(html_source_code)
        assert result == "UC_x5XG1OV2P6uZZ5FSM9Ttw"


def test_get_youtube_channel_id_script_tag():
        """
        Test case for extracting YouTube channel ID from a script tag.

        This test verifies that the `get_youtube_channel_id` function correctly extracts
        the channel ID from the 'ytInitialData' script tag in the provided HTML source code.

        Steps:
        1. Define the HTML source code containing the 'ytInitialData' script tag with the channel ID.
        2. Call the `get_youtube_channel_id` function with the HTML source code.
        3. Assert that the extracted channel ID matches the expected channel ID.
        """
        html_source_code = (
            b'<script>var ytInitialData = {"channel_id":"UC_x5XG1OV2P6uZZ5FSM9Ttw"};</script>'
        )
        result = get_youtube_channel_id(html_source_code)
        assert result == "UC_x5XG1OV2P6uZZ5FSM9Ttw"


def test_get_youtube_channel_id_not_found():
        """
        Test case for handling the scenario where the YouTube channel ID is not found in the HTML source code.

        This test verifies that the `get_youtube_channel_id` function returns None when the HTML source code
        does not contain a YouTube channel ID.

        Steps:
        1. Define the HTML source code that does not contain a YouTube channel ID.
        2. Call the `get_youtube_channel_id` function with the HTML source code.
        3. Assert that the returned result is None.
        """
        html_source_code = b"<html><head></head><body>No channel ID here</body></html>"
        result = get_youtube_channel_id(html_source_code)
        assert result is None


def test_get_youtube_channel_id_none_input():
    """
    Test case for handling None input when extracting YouTube channel ID.

    This test verifies that the `get_youtube_channel_id` function returns None
    when the input HTML source code is None.

    Steps:
    1. Call the `get_youtube_channel_id` function with None as the input.
    2. Assert that the returned result is None.
    """
    result = get_youtube_channel_id(None)
    assert result is None


def test_create_rss_feed_url_valid_channel_id():
    """
    Test case for creating a valid RSS feed URL with a given YouTube channel ID.

    This test verifies that the `create_rss_feed_url` function correctly constructs
    the RSS feed URL when provided with a valid YouTube channel ID.

    Steps:
    1. Define a valid YouTube channel ID.
    2. Call the `create_rss_feed_url` function with the channel ID.
    3. Assert that the returned URL matches the expected RSS feed URL.
    """
    channel_id = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
    result = create_rss_feed_url(channel_id)
    assert result == "https://www.youtube.com/feeds/videos.xml?channel_id=UC_x5XG1OV2P6uZZ5FSM9Ttw"


def test_create_rss_feed_url_empty_channel_id():
    """
    Test case for handling an empty YouTube channel ID when creating an RSS feed URL.

    This test verifies that the `create_rss_feed_url` function returns None
    when provided with an empty YouTube channel ID.

    Steps:
    1. Define an empty YouTube channel ID.
    2. Call the `create_rss_feed_url` function with the empty channel ID.
    3. Assert that the returned result is None.
    """
    channel_id = ""
    result = create_rss_feed_url(channel_id)
    assert result is None


def test_create_rss_feed_url_none_channel_id():
        """
        Test case for handling None as the YouTube channel ID when creating an RSS feed URL.

        This test verifies that the `create_rss_feed_url` function returns None
        when provided with a None YouTube channel ID.

        Steps:
        1. Call the `create_rss_feed_url` function with None as the channel ID.
        2. Assert that the returned result is None.
        """
        result = create_rss_feed_url(None)
        assert result is None


def test_fetch_rss_feed_content_success():
        """
        Test case for successfully fetching RSS feed content.

        This test mocks the `requests.get` method to simulate a successful HTTP GET request
        to an RSS feed URL. It verifies that the `fetch_rss_feed_content` function returns
        the expected parsed content when the request is successful.

        Steps:
        1. Define the RSS feed URL.
        2. Define the expected RSS feed content to be returned by the mocked request.
        3. Mock the `requests.get` method to return a successful response with the expected content.
        4. Call the `fetch_rss_feed_content` function with the feed URL.
        5. Assert that the returned content is not None.
        6. Assert that the length of the returned content is 2.
        7. Assert that the titles of the returned entries match the expected titles.
        """
        feed_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UC_x5XG1OV2P6uZZ5FSM9Ttw"
        expected_content = b"""<feed>
            <entry>
                <title>Video 1</title>
                <published>2023-10-01T00:00:00+00:00</published>
                <link href="https://www.youtube.com/watch?v=video1"/>
            </entry>
            <entry>
                <title>Video 2</title>
                <published>2023-10-02T00:00:00+00:00</published>
                <link href="https://www.youtube.com/watch?v=video2"/>
            </entry>
        </feed>"""

        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = expected_content

            result = fetch_rss_feed_content(feed_url)

            assert result is not None, "The result should not be None"
            assert len(result) == 2
            assert result[0].find("title").text == "Video 1"
            assert result[1].find("title").text == "Video 2"


def test_fetch_rss_feed_content_failure():
        """
        Test case for handling failure when fetching RSS feed content.

        This test mocks the `requests.get` method to simulate a failed HTTP GET request
        to an RSS feed URL. It verifies that the `fetch_rss_feed_content` function returns
        None when the request fails.

        Steps:
        1. Define the RSS feed URL.
        2. Mock the `requests.get` method to raise a `requests.exceptions.RequestException`.
        3. Call the `fetch_rss_feed_content` function with the feed URL.
        4. Assert that the returned result is None.
        """
        feed_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UC_x5XG1OV2P6uZZ5FSM9Ttw"

        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Mocked Exception")

            result = fetch_rss_feed_content(feed_url)
            assert result is None


def test_filter_videos_by_date():
        """
        Test case for filtering videos by date.

        This test verifies that the `filter_videos` function correctly filters
        the list of video entries based on the specified date.

        Steps:
        1. Define a list of video entries with different publication dates.
        2. Define the filter criteria (filter by date).
        3. Call the `filter_videos` function with the entries and filter criteria.
        4. Assert that the length of the filtered result is 1.
        5. Assert that the title of the filtered video matches the expected title.
        """
        entries = [
            BeautifulSoup(
                '<entry><title>Video 1</title><published>2023-10-01T00:00:00+00:00</published><link href="https://www.youtube.com/watch?v=video1"/></entry>',
                "xml",
            ),
            BeautifulSoup(
                '<entry><title>Video 2</title><published>2023-10-02T00:00:00+00:00</published><link href="https://www.youtube.com/watch?v=video2"/></entry>',
                "xml",
            ),
        ]
        filter_by = "date"
        filter_value = "2023-10-01"

        result = filter_videos(entries, filter_by, filter_value)
        assert len(result) == 1
        assert result[0]["title"] == "Video 1"


def test_filter_videos_by_title():
    """
    Test case for filtering videos by title.

    This test verifies that the `filter_videos` function correctly filters
    the list of video entries based on the specified title.

    Steps:
    1. Define a list of video entries with different titles.
    2. Define the filter criteria (filter by title).
    3. Call the `filter_videos` function with the entries and filter criteria.
    4. Assert that the length of the filtered result is 1.
    5. Assert that the title of the filtered video matches the expected title.
    """
    entries = [
        BeautifulSoup(
            '<entry><title>Python Tutorial</title><published>2023-10-01T00:00:00+00:00</published><link href="https://www.youtube.com/watch?v=video1"/></entry>',
            "xml",
        ),
        BeautifulSoup(
            '<entry><title>Cooking Show</title><published>2023-10-02T00:00:00+00:00</published><link href="https://www.youtube.com/watch?v=video2"/></entry>',
            "xml",
        ),
    ]
    filter_by = "title"
    filter_value = "Python"

    result = filter_videos(entries, filter_by, filter_value)
    assert len(result) == 1
    assert result[0]["title"] == "Python Tutorial"


def test_filter_videos_no_filter():
            """
            Test case for filtering videos without any filter criteria.

            This test verifies that the `filter_videos` function returns all video entries
            when no filter criteria are provided.

            Steps:
            1. Define a list of video entries with different publication dates and titles.
            2. Call the `filter_videos` function without any filter criteria.
            3. Assert that the length of the returned result is 2.
            4. Assert that the titles of the returned entries match the expected titles.
            """
            entries = [
                BeautifulSoup(
                    '<entry><title>Video 1</title><published>2023-10-01T00:00:00+00:00</published><link href="https://www.youtube.com/watch?v=video1"/></entry>',
                    "xml",
                ),
                BeautifulSoup(
                    '<entry><title>Video 2</title><published>2023-10-02T00:00:00+00:00</published><link href="https://www.youtube.com/watch?v=video2"/></entry>',
                    "xml",
                ),
            ]

            result = filter_videos(entries)
            assert len(result) == 2
            assert result[0]["title"] == "Video 1"
            assert result[1]["title"] == "Video 2"
