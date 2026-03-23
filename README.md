# Ozon Parser

A web scraper for Ozon.by that collects product information with configurable description fetching. Built with Playwright and Selectolax.

> ⚠️ **Note**: Collects 100 items in ~10 seconds, but fetching descriptions is significantly slower (~8 seconds per item)

## Features

- **Product Search**: Search Ozon.by for any product
- **Data Collection**: Gathers product names, ratings, review counts, prices, and URLs
- **Description Fetching**: Optional detailed product description retrieval (slow but detailed)
- **CSV Export**: Automatically saves results to CSV files in the `export/` directory
- **Configurable Limits**: Set maximum items to collect via command-line arguments
- **Asynchronous Architecture**: Uses asyncio for concurrent operations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dadaskis/ozon_parser.git
cd ozon_parser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

Run the main script:
```bash
python main.py
```

### Interactive Commands

The program accepts several arguments in your search query:

| Argument | Description |
|----------|-------------|
| `//desc` | Enable description fetching (⚠️ slow - ~8 seconds per item) |
| `//max:N` | Set maximum items to collect (default: 100) |
| `//exit` | Exit the program |

### Examples

```bash
# Basic search (100 items, no descriptions)
Enter item name to search: headphones

# Search with custom limit (50 items, no descriptions)
Enter item name to search: smartphone //max:50

# Search with descriptions (⚠️ slow!)
Enter item name to search: laptop //desc

# Search with both options
Enter item name to search: gaming mouse //max:200 //desc
```

## Performance

- **Collection**: ~100 items in 10 seconds (grid scraping only)
- **Description Fetching**: ~1 item per 8 seconds (individual page visits)
- **Total Time**: For 100 items with descriptions: ~13-14 minutes

The significant slowdown for descriptions is due to:
- Visiting each product's individual page
- Waiting for page loads
- Bot protection mechanisms

## Project Structure

```
ozon_parser/
├── main.py                 # Entry point and CLI
├── scraper.py             # Main orchestrator
├── searcher.py            # Grid search and parsing
├── desc_peeker.py         # Description fetching
├── collected_data.py      # Data storage and export
├── ozon_item.py           # Data model
├── config.py              # Logging configuration
├── requirements.txt       # Dependencies
└── export/                # Output directory (created automatically)
```

## Output

Results are saved as CSV files in the `export/` directory with the search term as filename:
- `export/headphones.csv`
- `export/smartphone.csv`

Each CSV contains:
- `name` - Product name
- `rating` - Product rating (0.0-5.0)
- `ratings_amount` - Number of reviews
- `price` - Product price
- `description` - Full description (or "Undefined" if not fetched)
- `url` - Product page URL

## Technical Details

- **Async/Await**: Fully asynchronous using `asyncio`
- **Browser Automation**: Playwright with stealth plugins to avoid detection
- **Parsing**: Selectolax for HTML parsing
- **Data Storage**: Pandas DataFrames with CSV export
- **Headless Mode**: Runs in headless Chromium by default

## Known Limitations

1. **Description Speed**: Fetching descriptions is intentionally slow to avoid triggering bot protection
2. **Bot Protection**: Ozon has active anti-bot measures; the stealth configuration helps but isn't perfect
3. **Rate Limiting**: Be respectful with request frequency to avoid IP blocks

## Contributing

Feel free to open issues or submit pull requests. Areas for improvement:
- Faster description fetching while maintaining stealth
- Better error handling and recovery
- Additional data fields
- Proxy support

## License

MIT License, *happiness to everyone!*

---

*"Because why not? Why not parsing a website with known inadequate security measures against everyone?"*
