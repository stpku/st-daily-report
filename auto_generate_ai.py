import os
import json
import datetime
import requests
import sys

import xml.etree.ElementTree as ET
import urllib.parse

# Load configuration
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config_secret.json')

def fetch_arxiv_papers():
    """Fetch recent papers from Arxiv related to GeoAI/World Models"""
    print("Fetching latest papers from Arxiv...")
    base_url = "http://export.arxiv.org/api/query"
    # Search for: (GeoAI OR "Remote Sensing" OR "World Model" OR "Spatio-Temporal") AND (submittedDate within last 3 days)
    # Arxiv API doesn't support easy date filtering in search_query, so we fetch recent and filter
    search_query = 'all:GeoAI OR all:"Remote Sensing" OR all:"World Model" OR all:"Spatio-Temporal"'
    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": 10,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        papers = []
        for entry in root.findall('atom:entry', ns):
            title_elem = entry.find('atom:title', ns)
            summary_elem = entry.find('atom:summary', ns)
            id_elem = entry.find('atom:id', ns)
            published_elem = entry.find('atom:published', ns)
            
            if title_elem is None or summary_elem is None or id_elem is None or published_elem is None:
                continue
                
            if title_elem.text and summary_elem.text and id_elem.text and published_elem.text:
                title = title_elem.text.strip().replace('\n', ' ')
                summary = summary_elem.text.strip().replace('\n', ' ')
                link = id_elem.text.strip()
                published = published_elem.text[:10]
                papers.append(f"- Title: {title}\n  Published: {published}\n  Link: {link}\n  Summary: {summary[:200]}...")
            
        return "\n\n".join(papers)
    except Exception as e:
        print(f"Failed to fetch Arxiv papers: {e}")
        return "No papers fetched (Error accessing Arxiv)."

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file not found at {CONFIG_FILE}")
        print("Please create it with your API keys.")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_content(config, date_str, papers_context):
    api_url = f"{config['api_base_url'].rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """You are an expert AI editor for a 'GeoAI + World Model' Daily Dashboard.
Your goal is to generate a high-quality, professional daily report in Markdown format.
Focus areas:
1. GeoAI (Spatial Intelligence, Remote Sensing, GIS + AI)
2. World Models (3D Generation, General Simulation, Embodied AI)

Format requirements:
- Language: Chinese (Simplified)
- Structure:
  - Header (Date, Scope, Priorities)
  - A. Top Papers (Use the provided Arxiv papers context. Select the most relevant 5-8 papers. Translate titles to Chinese but keep original English title in brackets if needed. Add 'One-line Insight'.)
  - B. Industry News (Generate 3-5 realistic industry updates based on general knowledge of Tech Giants like Google, NVIDIA, Microsoft in this field)
  - C. Open Source Projects (Suggest relevant open source projects)
  - D. 3 New Ideas (Creative fusion of GeoAI + World Model)
- Style: Concise, professional, insightful."""

    user_prompt = f"""Generate the GeoAI Daily Dashboard for date: {date_str}.

Here is the latest Arxiv Papers context:
{papers_context}

Please create a structure like this:

# GeoAI + 世界模型 紧凑型仪表盘
Date: {date_str}
Scope: GeoAI (空间智能) + World Model (3D生成与模拟)
...
"""

    payload = {
        "model": config.get("model", "gpt-3.5-turbo"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }


    response = None
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"API Call Failed: {e}")
        if response is not None:
            print(f"Status Code: {response.status_code}")
            print(f"Response Content: {response.text[:500]}...")
        return None

def main():
    config = load_config()
    today = datetime.date.today().isoformat()
    
    papers_context = fetch_arxiv_papers()
    
    print(f"Generating report for {today} using model {config.get('model')}...")
    content = generate_content(config, today, papers_context)
    
    if content:
        output_dir = "/mnt/d/04_代码/code/sandbox/doc/view"
        filename = f"geoai_world-model_dashboard_{today}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Successfully generated: {filepath}")
    else:
        print("Failed to generate content.")

if __name__ == "__main__":
    main()
