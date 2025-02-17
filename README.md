# YouTube Channel to RSS Feed

This script converts a YouTube channel URL to an RSS feed URL and fetches the latest videos from the channel. It can also filter videos by date or title.

## Features

- Fetch YouTube channel source code
- Extract channel ID from the source code
- Create RSS feed URL from the channel ID
- Fetch and parse RSS feed content
- Filter videos by date or title
- Copy RSS feed URL to clipboard

## Requirements

- Python 3.x
- `requests` library
- `beautifulsoup4` library
- `lxml` library (for XML parsing)
- `pyperclip` library

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/youtube_channel_to_rss.git
    cd youtube_channel_to_rss
    ```

2. Install the required libraries:
    ```sh
    pip install requests beautifulsoup4 lxml pyperclip
    ```

## Usage

Run the script with the YouTube channel URL as an argument. Optionally, you can filter videos by date or title.

```sh
python main.py <youtube_channel_url> [--filter_by date|title] [--filter_value <value>]
```

### Examples

Fetch the latest videos from a YouTube channel:
```sh
python main.py https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw
```

Fetch videos published on a specific date:
```sh
python main.py https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw --filter_by date --filter_value 2023-10-01
```

Fetch videos with a specific keyword in the title:
```sh
python main.py https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw --filter_by title --filter_value "keyword"
```

## Creating an Executable

You can create an executable from the Python script using PyInstaller. This allows you to run the script without needing a Python interpreter.

1. Install PyInstaller:
    ```sh
    pip install pyinstaller
    ```

2. Create the executable:
    ```sh
    pyinstaller --onefile main.py
    ```

3. The executable will be created in the `dist` directory.

### Running the Executable

Run the executable with the YouTube channel URL as an argument. Optionally, you can filter videos by date or title.

```sh
./dist/main <youtube_channel_url> [--filter_by date|title] [--filter_value <value>]
```

### Examples

Fetch the latest videos from a YouTube channel:
```sh
./dist/main https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw
```

Fetch videos published on a specific date:
```sh
./dist/main https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw --filter_by date --filter_value 2023-10-01
```

Fetch videos with a specific keyword in the title:
```sh
./dist/main https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw --filter_by title --filter_value "keyword"
```

## License

This project is licensed under the MIT License.
