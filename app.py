from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import threading
import time
import os
from job_scraper import scrape_linkedin_jobs, save_links_to_file

app = Flask(__name__)

SCRAPE_STATUS = {'running': False, 'message': '', 'filename': ''}

def background_scrape(roles, locations, filename):
    SCRAPE_STATUS['running'] = True
    SCRAPE_STATUS['message'] = f"Scraping jobs for roles: {', '.join(roles)} at locations: {', '.join(locations)}..."
    SCRAPE_STATUS['filename'] = ''
    all_links = []
    try:
        for role in roles:
            SCRAPE_STATUS['message'] = f"Scraping jobs for '{role}' at {', '.join(locations)}..."
            links = scrape_linkedin_jobs(role, locations)
            all_links.extend(links)
            time.sleep(2)
        save_links_to_file(all_links, roles, locations, filename)
        SCRAPE_STATUS['message'] = f"Done! Found {len(all_links)} jobs."
        SCRAPE_STATUS['filename'] = filename
    except Exception as e:
        SCRAPE_STATUS['message'] = f"Error: {e}"
    SCRAPE_STATUS['running'] = False

@app.route('/', methods=['GET'])
def index():
    return render_template('job_scraper.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    if SCRAPE_STATUS['running']:
        return redirect(url_for('index'))
    roles = request.form['roles'].replace('\r', '').replace('\n', ',').split(',')
    roles = [r.strip() for r in roles if r.strip()]
    locations = request.form['locations'].replace('\r', '').replace('\n', ',').split(',')
    locations = [l.strip() for l in locations if l.strip()]
    filename = f"scraped_jobs_{int(time.time())}.html"
    threading.Thread(target=background_scrape, args=(roles, locations, filename)).start()
    SCRAPE_STATUS['message'] = "Started scraping..."
    SCRAPE_STATUS['filename'] = ''
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join('result', filename)
    return send_file(path, as_attachment=False)

@app.route('/status')
def status():
    return jsonify(SCRAPE_STATUS)

if __name__ == '__main__':
    app.run(debug=True) 