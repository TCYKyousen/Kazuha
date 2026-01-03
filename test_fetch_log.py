import requests
import json
import re

def test_fetch_release():
    repo_owner = "Haraguse"
    repo_name = "Kazuha"
    tag_name = "v1.0.5.0"
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/tags/{tag_name}"
    print(f"Fetching {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            body = data.get('body', '')
            print(f"Successfully fetched release: {data.get('name')}")
            print(f"Body length: {len(body)}")
            print("Body preview:")
            print("-" * 20)
            print(body[:200])
            print("-" * 20)
            
            import markdown
            html = markdown.markdown(body, extensions=['fenced_code', 'tables', 'nl2br'])
            print(f"Markdown converted HTML length: {len(html)}")
            print("HTML preview:")
            print("-" * 20)
            print(html[:200])
            print("-" * 20)
        else:
            print(f"Failed to fetch: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch_release()
