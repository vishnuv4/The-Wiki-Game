import requests
import time
from bs4 import BeautifulSoup
import random
import os
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style
import sys

HOPS = 2

def get_soup_from_url(url):
    response = requests.get(url)
    response_url = response.url
    soup = BeautifulSoup(response.content, 'html.parser')
    return (soup, response_url)

def get_title(soup):
    title = soup.find(id="firstHeading").text
    return title

def find_and_shuffle_links(soup):
    all_links = soup.find(id="bodyContent").find_all("a")
    random.seed(os.urandom(16))  
    for _ in range(5):
        random.shuffle(all_links)

    return all_links

def write_soup_to_file(soup, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(soup.prettify())

def get_next_link(shuffled_links):
    for link in shuffled_links:
        if link.get('href', '').startswith("/wiki/") and ":" not in link['href']:
            full_link = "https://en.wikipedia.org" + link['href']
            return (full_link, link.text.strip())
    
    return None

page_ctr = 0
def scrape_wikipedia_article(url, pages):
    soup, response_url = get_soup_from_url(url)
    title = get_title(soup)
    shuffled_links = find_and_shuffle_links(soup)
    next_link, link_text = get_next_link(shuffled_links)

    global page_ctr
    write_soup_to_file(soup, f"game1\\page{page_ctr}.html")
    page_ctr += 1

    pages[title] = [response_url, link_text]

    return next_link

def wikipedia_crawler(max_hops):
    pages = {}
    start_url = scrape_wikipedia_article(f"https://en.wikipedia.org/wiki/Special:Random", pages)
    current_url = start_url

    print(f"\nGet from the first link to the second in {HOPS} hops!\n")

    print(f"{Fore.LIGHTBLACK_EX}")
    for i in range(max_hops):
        current_url = scrape_wikipedia_article(current_url, pages)
        print(f"Loaded page {i+1}...")
        time.sleep(1)
    
    print("Loading complete.")
    print(f"{Style.RESET_ALL}")

    # Extract first and last entries
    first_key = list(pages)[0]
    first_url = pages[first_key][0]
    last_key = list(pages)[-1]
    last_url = pages[last_key][0]

    # Create a DataFrame with START and END labels
    data = {
        "POSITION": ["START", "END"],
        "PAGE TITLE": [first_key, last_key],
        "PAGE LINK": [first_url, last_url]
    }

    df = pd.DataFrame(data)

    print(f"{Fore.MAGENTA}")
    print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))

    print(f"{Fore.BLUE}")
    print_section(3)
    i = 0
    while True:
        text = input(">> ")
        match text:
            case "":
                break
            case "hint" | "h":
                if i < len(pages) - 1:
                    print(f"{Fore.GREEN}")
                    print(pages[list(pages)[i]][1])
                    print(f"{Fore.BLUE}")
                    i += 1
                else:
                    print(f"{Fore.YELLOW}No more hints!{Fore.BLUE}")
            case _:
                print("Invalid input. Try again.")

    table_data = []
    for i, (k, v) in enumerate(pages.items()):
        if i < len(pages) - 1:
            table_data.append({
                "PAGE TITLE": k,
                "PAGE LINK": v[0],
                "NEXT LINK TEXT": v[1]
            })
        else:
            table_data.append({
                "PAGE TITLE": k,
                "PAGE LINK": v[0],
                "NEXT LINK TEXT": ""
            })
    df = pd.DataFrame(table_data)
    print(f"{Fore.GREEN}")
    print(tabulate(df, headers='keys', tablefmt='psql'))
    print(f"{Style.RESET_ALL}")

def print_section(section_num: int):
    with open("text.txt", "r") as file:
        readlines = file.readlines()
    
    lines = [l[:-1] for l in readlines]

    print_lines = []
    print_flag = False
    for line in lines:
        if line != '' and line[0] == "#":
            if int(line[1]) == section_num:
                print_flag = True
            else:
                print_flag = False
            continue
        
        if print_flag:
            print(f"{line:^50}")
    
if __name__ == "__main__":
    print(f"{Style.RESET_ALL}")
    print(f"{Fore.BLUE}")
    print_section(1)
    print(f"{Fore.CYAN}")
    print_section(4)
    wikipedia_crawler(HOPS)
    print(f"{Fore.CYAN}")
    print_section(2)
    print(50*"=")
    print()