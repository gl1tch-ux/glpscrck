# glpscrck

GLPSCRCK - A Powerful Password Cracker Tool

**GLPSCRCK** is a powerful password cracker tool designed to perform both **brute-force** attacks and **generate** custom wordlists based on user-provided inputs. It supports multiple platforms and provides logging for efficient tracking of attempts.

## Features

- **Brute Force Attack**: Attempts login with username/password combinations.
- **Wordlist Generation**: Creates custom password lists from a given set of words and adds special characters and numbers.
- **Logging**: Logs successful and failed login attempts to a file for later analysis.
- **Progress Bars**: Provides real-time feedback using `tqdm` for both brute-force and wordlist generation.

## Requirements

- Python 3.x
- `requests`
- `tqdm`
- `colorama`

To install the necessary dependencies, create a `requirements.txt` file and install using `pip`:

```bash
pip install -r requirements.txt

requirements.txt:

requests
tqdm
colorama

Usage

You can run the tool in one of two modes: attack (for brute-force login attempts) or generate (to generate a custom wordlist).

1. Attack Mode (attack)

To run a brute-force attack:

python3 glpscrck.py attack -u <username> -P <password_file> -l <login_url> -m <method> -t <timeout> -d <delay>

Options:

-u <username>: Single username for brute-force (or use -U with a wordlist).

-P <password_file>: Path to a password wordlist (or use -p for a single password).

-l <login_url>: Target login URL.

-m <method>: Request method (POST/GET), default is POST.

-t <timeout>: Timeout for requests in seconds (default is 10).

-d <delay>: Delay between attempts in seconds (default is 1).


2. Wordlist Generation Mode (generate)

To generate a custom password wordlist based on a set of input words:

python3 glpscrck.py generate -W <comma_separated_words> -o <output_file>

Options:

-W <comma_separated_words>: Words used to generate passwords (e.g., admin,root,password).

-o <output_file>: Output file for saving the generated wordlist (default is generated_passwords.txt).


Example Commands:

Brute Force Attack Example:

python3 glpscrck.py attack -u admin -P passwords.txt -l http://example.com/login -m POST -t 10 -d 1

Wordlist Generation Example:

python3 glpscrck.py generate -W admin,root,password123 -o custom_wordlist.txt

Logging

All attempts (successful and failed) will be logged in the file glpscrck.log.

Disclaimer

GLPSCRCK should only be used for ethical purposes.

Unauthorized access to systems is illegal and unethical.

Always have explicit permission before testing any systems with this tool.

GLPSCRCK is intended for educational purposes only.
