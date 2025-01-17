# Domain Checker Pro 🔍

A powerful domain availability checker tool that allows you to check the availability of multiple .com domains simultaneously. Built with Python and Streamlit, this tool offers both bulk checking capabilities and single domain lookup features.

## Features ✨

- **Bulk Domain Checking**: Upload a text file with multiple domain names
- **Single Domain Lookup**: Quick check for individual domains
- **Clean Interface**: User-friendly Streamlit web interface
- **Export Results**: Download results as CSV file
- **Real-time Progress**: Live progress tracking for bulk checks
- **Error Handling**: Robust error management for reliable results

## Installation 🛠️

1. Clone the repository:
```bash
git clone https://github.com/geethikaisuru/Domain-Checker.git
cd Domain-Checker
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage 💡

### Web Interface (Recommended)

Run the Streamlit app:
```bash
streamlit run domain_checker_app.py
```

This will open a web interface where you can:
- Upload a text file for bulk domain checking
- Check individual domains
- Download results as CSV

### Command Line Interface

Run the command-line version:
```bash
python main.py
```

Make sure to have a `try.txt` file in the same directory with domain names (one per line).

## Input Format 📝

- Create a text file with one domain name per line
- Domain names should be written without the .com extension
- Example:
  ```
  mydomain
  mystartup
  mycompany
  ```

## Output Files 📂

The tool generates two files:
- `available.txt`: List of available domains
- `notAvailable.txt`: List of already registered domains

## Technical Details 🔧

- Uses Python's `whois` library for domain lookups
- Implements rate limiting to avoid API restrictions
- Handles various edge cases and errors
- Cleans and validates domain names before checking

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## Author ✍️

**Geethika Isuru**
- LinkedIn: [geethikaisuru](https://www.linkedin.com/in/geethikaisuru/)
- GitHub: [geethikaisuru](https://github.com/geethikaisuru)

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ by Geethika Isuru