import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
from urllib.parse import urljoin
import random
from fake_useragent import UserAgent
import os

def get_random_user_agent():
    ua = UserAgent()
    return ua.random

def create_session():
    session = requests.Session()
    session.headers.update({
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    })
    return session

def scrape_indeed_jobs(keyword, locations, max_pages=3):
    base_url = "https://www.indeed.com/jobs"
    job_links = []
    session = create_session()

    for location in locations:
        for page in range(max_pages):
            query_params = {
                "q": keyword,
                "l": location,
                "start": page * 10
            }
            url = f"{base_url}?{urllib.parse.urlencode(query_params)}"
            try:
                session.headers.update({'User-Agent': get_random_user_agent()})
                response = session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.find_all("div", class_="jobsearch-SerpJobCard")
                if not job_cards:
                    break

                for card in job_cards:
                    link = card.find("a", class_="jobtitle")
                    if link and link.get("href"):
                        full_link = urljoin("https://www.indeed.com", link['href'])
                        job_links.append((full_link, location))

                print(f"Indeed: Scraped page {page + 1} for {keyword} in {location}")
                time.sleep(random.uniform(2, 4))  # Random delay between 2-4 seconds

            except requests.RequestException as e:
                print(f"Indeed: Error on page {page + 1} for {location}: {e}")
                time.sleep(random.uniform(5, 10))  # Longer delay on error
                continue

    return job_links

def scrape_linkedin_jobs(keyword, locations, max_pages=1):
    base_url = "https://www.linkedin.com/jobs/search/"
    job_links = []
    session = create_session()

    for location in locations:
        for page in range(max_pages):
            query_params = {
                "keywords": keyword,
                "location": location,
                "start": page * 25
            }
            url = f"{base_url}?{urllib.parse.urlencode(query_params)}"
            try:
                session.headers.update({'User-Agent': get_random_user_agent()})
                response = session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.find_all("a", class_="base-card__full-link")
                if not job_cards:
                    break

                for card in job_cards:
                    if card.get("href"):
                        job_links.append((card['href'], location))

                print(f"LinkedIn: Scraped page {page + 1} for {keyword} in {location}")
                time.sleep(random.uniform(3, 5))  # Random delay between 3-5 seconds

            except requests.RequestException as e:
                print(f"LinkedIn: Error on page {page + 1} for {location}: {e}")
                time.sleep(random.uniform(5, 10))  # Longer delay on error
                continue

    return job_links

def scrape_glassdoor_jobs(keyword, locations, max_pages=2):
    base_url = "https://www.glassdoor.com/Job/jobs.htm"
    job_links = []
    session = create_session()

    for location in locations:
        for page in range(max_pages):
            query_params = {
                "suggestCount": 0,
                "suggestChosen": "false",
                "clickSource": "searchBtn",
                "typedKeyword": keyword,
                "locT": "C",
                "locName": location,
                "jobType": "",
                "fromAge": 0,
                "radius": 0,
                "page": page + 1
            }
            url = f"{base_url}?{urllib.parse.urlencode(query_params)}"
            try:
                session.headers.update({'User-Agent': get_random_user_agent()})
                response = session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.find_all("a", class_="jobLink")
                if not job_cards:
                    break

                for card in job_cards:
                    if card.get("href"):
                        full_link = urljoin("https://www.glassdoor.com", card['href'])
                        job_links.append((full_link, location))

                print(f"Glassdoor: Scraped page {page + 1} for {keyword} in {location}")
                time.sleep(random.uniform(3, 5))  # Random delay between 3-5 seconds

            except requests.RequestException as e:
                print(f"Glassdoor: Error on page {page + 1} for {location}: {e}")
                time.sleep(random.uniform(5, 10))  # Longer delay on error
                continue

    return job_links

def save_links_to_file(links, filename="sdet_jobs.html"):
    # Ensure the html directory exists
    html_dir = "result"
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)
    filepath = os.path.join(html_dir, filename) if not filename.startswith(html_dir + os.sep) else filename
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SDET Job Postings</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background-color: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            }
            th, td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #4CAF50;
                color: white;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            .checkbox-cell {
                text-align: center;
            }
            .checkbox {
                width: 20px;
                height: 20px;
                cursor: pointer;
            }
            .checked-row {
                background-color: #e8f5e9;
            }
        </style>
        <script>
            function toggleRow(row) {
                const checkbox = row.querySelector('.checkbox');
                const isChecked = checkbox.checked;
                row.classList.toggle('checked-row', isChecked);
                
                // Save the state to localStorage
                const jobId = row.getAttribute('data-job-id');
                localStorage.setItem(jobId, isChecked);
            }

            // Restore checkbox states when page loads
            window.onload = function() {
                const rows = document.querySelectorAll('tr[data-job-id]');
                rows.forEach(row => {
                    const jobId = row.getAttribute('data-job-id');
                    const isChecked = localStorage.getItem(jobId) === 'true';
                    const checkbox = row.querySelector('.checkbox');
                    checkbox.checked = isChecked;
                    if (isChecked) {
                        row.classList.add('checked-row');
                    }
                });
            }
        </script>
    </head>
    <body>
        <h1>SDET Job Postings</h1>
        <table>
            <tr>
                <th>Job Role</th>
                <th>Location</th>
                <th>Job Link</th>
                <th>Checked</th>
            </tr>
    """

    for index, (link, location) in enumerate(links):
        # Extract job role from the URL or use a default
        job_role = "SDET"  # Default value
        if "SDET2" in link:
            job_role = "SDET2"
        elif "SDET-II" in link:
            job_role = "SDET-II"
        elif "Software+Development+Engineer+in+Test" in link:
            job_role = "Software Development Engineer in Test"

        html_content += f"""
            <tr data-job-id="job-{index}">
                <td>{job_role}</td>
                <td>{location}</td>
                <td><a href="{link}" target="_blank">View Job</a></td>
                <td class="checkbox-cell">
                    <input type="checkbox" class="checkbox" onchange="toggleRow(this.parentElement.parentElement)">
                </td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved {len(links)} job links to {filepath}")

if __name__ == "__main__":
    keywords = ["SDET", "SDET2", "Software Development Engineer in Test", "Software Engineer in Test"]
    locations = ["Bangalore, Karnataka, India"]
    all_links = []

    for keyword in keywords:
        print(f"Scraping for keyword: {keyword}")
        # indeed_links = scrape_indeed_jobs(keyword, locations)
        linkedin_links = scrape_linkedin_jobs(keyword, locations)
        # glassdoor_links = scrape_glassdoor_jobs(keyword, locations)
        # all_links.extend(indeed_links)
        all_links.extend(linkedin_links)
        # all_links.extend(glassdoor_links)
        time.sleep(random.uniform(5, 10))  # Delay between keywords

    save_links_to_file(all_links)