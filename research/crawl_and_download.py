import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse, unquote

BASE_URL = "https://kkucommed.kku.ac.th/"
DOWNLOAD_DIR = "D:/00 POND/University/Y3/COMMED/research/downloads/"
REPORT_FILE = "D:/00 POND/University/Y3/COMMED/research/kkucommed-site-docs.md"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

DOC_EXTENSIONS = ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')

visited_urls = set()
downloaded_files = []
errors = []

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "th-TH,th;q=0.9,en;q=0.8",
}

def sanitize_filename(name, max_len=80):
    """Sanitize a filename for Windows: strip illegal chars, replace spaces, truncate."""
    name = unquote(name)  # Decode percent-encoded characters
    illegal = '<>:"/\\|?*\r\n\t'
    for ch in illegal:
        name = name.replace(ch, '_')
    name = name.replace(' ', '_')
    # Truncate to avoid Windows path-length errors; keep extension
    if len(name) > max_len:
        stem, ext = os.path.splitext(name)
        name = stem[:max_len - len(ext)] + ext
    return name

def fetch_page(url):
    print(f"Fetching: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        errors.append(f"Fetch error: {url} -- {e}")
        return None

def download_file(url, target_path):
    print(f"Downloading {url}")
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=60)
        response.raise_for_status()
        with open(target_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        size = os.path.getsize(target_path)
        print(f"Downloaded: {target_path} ({size} bytes)")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        errors.append(f"Download error: {url} -- {e}")
        return False
    except OSError as e:
        print(f"OS error saving {target_path}: {e}")
        errors.append(f"Save error: {target_path} -- {e}")
        return False

def crawl_site(start_url, max_depth=3):
    queue = [(start_url, 0)]

    while queue:
        current_url, depth = queue.pop(0)

        if current_url in visited_urls or depth > max_depth:
            continue

        visited_urls.add(current_url)
        html_content = fetch_page(current_url)

        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')

            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(current_url, href)
                parsed_absolute_url = urlparse(absolute_url)

                # Stay on KKU COM MED or kku.ac.th domains
                if 'kku.ac.th' in parsed_absolute_url.netloc:
                    raw_name = os.path.basename(parsed_absolute_url.path)
                    file_extension = os.path.splitext(raw_name)[1].lower()

                    if file_extension in DOC_EXTENSIONS:
                        safe_name = sanitize_filename(raw_name)
                        local_path = os.path.join(DOWNLOAD_DIR, safe_name)
                        if not os.path.exists(local_path):
                            if download_file(absolute_url, local_path):
                                downloaded_files.append({
                                    'name': safe_name,
                                    'source_url': absolute_url,
                                    'local_path': local_path,
                                    'description': link.get_text(strip=True),
                                    'parent_page': current_url,
                                })
                    elif parsed_absolute_url.path.endswith('/') or not file_extension:
                        if absolute_url not in visited_urls:
                            queue.append((absolute_url, depth + 1))

def generate_report():
    NL = chr(10)
    lines = []
    lines.append("# KKU Community Medicine Site Documents")
    lines.append("")
    lines.append("This report details important documents and files found on the KKU Community Medicine department website.")
    lines.append(f"Crawled on: 2026-09-12")
    lines.append(f"Base URL: {BASE_URL}")
    lines.append(f"Total pages visited: {len(visited_urls)}")
    lines.append("")

    local_project_files = [
        "คู่มือการฝึกภาคสนามร่วมฯ2569.pdf",
        "รับน้อง MD52.xlsx",
        "รายชื่อนักศึกษาCOMMED2569.xlsx",
        "รายชื่อนักศึกษาCOMMED2569_ชื่อเล่น.xlsx",
        "full.md",
        "sheets_overview.txt",
        "target_overview.txt"
    ]
    local_project_dir = "D:/00 POND/University/Y3/COMMED/"

    lines.append(f"## Pages Crawled ({len(visited_urls)} pages)")
    lines.append("")
    for url in sorted(visited_urls):
        lines.append(f"- {url}")
    lines.append("")

    if errors:
        lines.append("## Errors Encountered")
        lines.append("")
        for err in errors:
            lines.append(f"- {err}")
        lines.append("")

    if downloaded_files:
        lines.append(f"## Downloaded Documents ({len(downloaded_files)} files)")
        lines.append("")
        for doc in downloaded_files:
            lines.append(f"### {doc['name']}")
            lines.append(f"- **Source URL:** [{doc['source_url']}]({doc['source_url']})")
            lines.append(f"- **Local Path:** `{doc['local_path']}`")
            lines.append(f"- **Description (from link text):** {doc['description']}")
            lines.append(f"- **Parent page:** {doc['parent_page']}")
            lines.append(f"- **Cross-link:** [To be filled in after content review]")
            lines.append("")
    else:
        lines.append("## No documents were found or downloaded.")
        lines.append("")

    lines.append("## Cross-reference with Existing Local Files")
    lines.append("")
    for local_file in local_project_files:
        lines.append(f"### {local_file}")
        lines.append(f"- **Local Path:** `{os.path.join(local_project_dir, local_file)}`")
        found_match = False
        for downloaded_doc in downloaded_files:
            if downloaded_doc['name'] == local_file:
                lines.append(f"- **Relationship:** Filename matches downloaded file at [{downloaded_doc['source_url']}]({downloaded_doc['source_url']})")
                found_match = True
                break
        if not found_match:
            lines.append("- **Relationship:** No exact filename match found among downloaded documents.")
        lines.append("")

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(NL.join(lines))

    print(f"Report generated: {REPORT_FILE}")

if __name__ == "__main__":
    crawl_site(BASE_URL)
    generate_report()
