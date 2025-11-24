# YouTube Channel to RSS Feed

This script converts a YouTube channel URL to an RSS feed URL and fetches the latest videos from the channel. It supports advanced filtering, multiple output formats, and intelligent caching for improved performance.

## Features

### Core Features
- **Fetch YouTube channel source code** - Supports both legacy channel IDs and modern @handle URLs
- **Extract channel ID** - Automatically detects channel ID from various YouTube URL formats
- **Create RSS feed URL** - Generates the RSS feed URL from the channel ID
- **Fetch and parse RSS feed content** - Retrieves and parses the latest videos from the channel
- **Multiple output formats** - Export results as text, JSON, or CSV
- **Clipboard integration** - Automatically copy RSS feed URL to clipboard

### Filtering Options
- **Filter by date** - Filter videos published on a specific date (exact match)
- **Filter by title** - Filter videos containing specific keywords in the title
- **Date range filtering** - Filter videos published after/before specific dates (`--after`, `--before`)
- **Duration filtering** - Filter videos by length using `--min-duration` and `--max-duration` (in seconds)
- **Multiple filters** - Combine multiple filters using AND logic for precise results

### Performance & Reliability
- **Intelligent caching** - Cache channel IDs locally to reduce network requests
- **Retry logic** - Automatic retry with exponential backoff for transient network failures
- **Configurable video limit** - Control how many videos to fetch (default: 5)

### Convenience Features
- **YouTube Handle support** - Works with modern `@username` URLs
- **Direct channel ID input** - Skip URL parsing by providing channel ID directly
- **Quiet mode** - Suppress informational messages for scripting use cases
- **Dry run mode** - Preview what would be fetched without making actual requests
- **Save to file** - Save RSS URL to file instead of clipboard for automation
- **Better error messages** - Detailed error messages with actionable suggestions
- **Version information** - Check the version with `--version`

## Requirements

- Python 3.9+
- `requests` library
- `beautifulsoup4` library
- `lxml` library (for XML parsing)
- `pyperclip` library

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/mberetvas/YoutubeChannel2rss.git
    cd YoutubeChannel2rss
    ```

2. Install the required libraries:
    ```sh
    pip install -r src/requirements.txt
    ```

## Usage

### Basic Usage

```sh
python src/main.py <youtube_channel_url>
```

### Command-Line Options

```
usage: main.py [-h] [--version] [--filter_by {date,title}] [--filter_value FILTER_VALUE]
               [--limit LIMIT] [--quiet] [--save-url FILENAME] [--output {text,json,csv}]
               [--after DATE] [--before DATE] [--channel-id ID] [--dry-run]
               [--no-cache] [--clear-cache]
               [youtube_url]

positional arguments:
  youtube_url           The YouTube channel URL (supports @handle or /channel/UC... format)

options:
  -h, --help            Show help message and exit
  --version, -v         Show program version and exit
  --filter_by {date,title}
                        Filter videos by date or title
  --filter_value FILTER_VALUE
                        Value to filter videos by (date: YYYY-MM-DD, title: keyword)
  --limit LIMIT         Maximum number of videos to fetch (default: 5)
  --quiet, -q           Suppress informational messages
  --save-url FILENAME   Save RSS feed URL to file instead of clipboard
  --output {text,json,csv}
                        Output format for video list (default: text)
  --after DATE          Filter videos published after this date (YYYY-MM-DD)
  --before DATE         Filter videos published before this date (YYYY-MM-DD)
  --channel-id ID       Directly provide the YouTube channel ID (skips URL parsing)
  --dry-run             Preview what would be fetched without making requests
  --no-cache            Disable channel ID caching
  --clear-cache         Clear the channel ID cache and exit
  --min-duration SECONDS
                        Filter videos with minimum duration in seconds
  --max-duration SECONDS
                        Filter videos with maximum duration in seconds
  --show-duration       Include video duration in the output
```

## Examples

### Basic Examples

Fetch the latest 5 videos from a YouTube channel:
```sh
python src/main.py https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw
```

Fetch the latest videos from a channel using the modern @handle format:
```sh
python src/main.py https://www.youtube.com/@channelname
```

### Filtering Examples

Filter videos published on a specific date:
```sh
python src/main.py https://www.youtube.com/@channelname --filter_by date --filter_value 2023-10-01
```

Filter videos with a specific keyword in the title:
```sh
python src/main.py https://www.youtube.com/@channelname --filter_by title --filter_value "Python"
```

Filter videos published in a date range:
```sh
python src/main.py https://www.youtube.com/@channelname --after 2023-10-01 --before 2023-10-31
```

Combine title and date range filters:
```sh
python src/main.py https://www.youtube.com/@channelname --filter_by title --filter_value "tutorial" --after 2023-10-01
```

### Output Format Examples

Export video list as JSON:
```sh
python src/main.py https://www.youtube.com/@channelname --output json
```

Export video list as CSV:
```sh
python src/main.py https://www.youtube.com/@channelname --output csv
```

### Advanced Examples

Fetch more videos (e.g., 15 instead of default 5):
```sh
python src/main.py https://www.youtube.com/@channelname --limit 15
```

Show video duration in the output:
```sh
python src/main.py https://www.youtube.com/@channelname --show-duration
```

Filter videos by minimum duration (e.g., longer than 10 minutes = 600 seconds):
```sh
python src/main.py https://www.youtube.com/@channelname --min-duration 600
```

Filter videos by maximum duration (e.g., shorter than 5 minutes = 300 seconds):
```sh
python src/main.py https://www.youtube.com/@channelname --max-duration 300
```

Combine duration filters (e.g., videos between 5-15 minutes):
```sh
python src/main.py https://www.youtube.com/@channelname --min-duration 300 --max-duration 900 --show-duration
```

Save RSS URL to a file for automation:
```sh
python src/main.py https://www.youtube.com/@channelname --save-url channel_rss.txt
```

Use quiet mode for scripting (suppress info messages):
```sh
python src/main.py https://www.youtube.com/@channelname --quiet --output json > videos.json
```

Directly provide channel ID (skips URL fetching):
```sh
python src/main.py --channel-id UC_x5XG1OV2P6uZZ5FSM9Ttw
```

Preview what would be fetched (dry run):
```sh
python src/main.py https://www.youtube.com/@channelname --dry-run --limit 10
```

Disable caching for a single run:
```sh
python src/main.py https://www.youtube.com/@channelname --no-cache
```

Clear the channel ID cache:
```sh
python src/main.py --clear-cache
```

## Caching

The script automatically caches channel IDs to improve performance on subsequent runs. The cache is stored in `~/.youtuberss/cache.json`.

- **Automatic caching**: Channel IDs are cached after the first successful fetch
- **Fast lookups**: Cached channels skip the URL fetching step
- **Manual control**: Use `--no-cache` to bypass cache or `--clear-cache` to reset

## Creating an Executable

You can create an executable from the Python script using PyInstaller. This allows you to run the script without needing a Python interpreter.

1. Install PyInstaller:
    ```sh
    pip install pyinstaller
    ```

2. Create the executable:
    ```sh
    cd src
    pyinstaller --onefile main.py
    ```

3. The executable will be created in the `src/dist` directory.

### Running the Executable

Run the executable with the same command-line options as the Python script:

```sh
./src/dist/main https://www.youtube.com/@channelname --limit 10 --output json
```

## Error Handling

The script provides detailed error messages with actionable suggestions:

- **Network timeouts**: Automatic retry with exponential backoff (up to 3 attempts)
- **404 errors**: Clear indication that the channel or feed was not found
- **Rate limiting**: Helpful message when YouTube rate limits are hit
- **Invalid URLs**: Suggestions for correct URL formats

## License

This project is licensed under the MIT License.
