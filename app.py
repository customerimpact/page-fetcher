import streamlit as st
import concurrent.futures
from scraper import scrape_single_page
import time

st.set_page_config(page_title="Page Fetcher & Knowledge Bundler", layout="wide")

st.title("Build Your AI Knowledge Base")
st.markdown("""
This tool allows you to scrape multiple web pages concurrently and bundle them into a single Markdown file.
Useful for creating training datasets or RAG contexts.
""")

# Input
urls_input = st.text_area("Enter URLs (one per line)", height=200, help="Paste a list of URLs here, separated by newlines.")

if st.button("Start Scraping", type="primary"):
    urls = [line.strip() for line in urls_input.split('\n') if line.strip()]
    
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        st.info(f"Starting scrape for {len(urls)} pages...")
        
        # Containers for status updates
        status_containers = {url: st.empty() for url in urls}
        results = []
        
        # Initialize status
        for url, container in status_containers.items():
            container.markdown(f"⏳ **Pending**: `{url}`")
            
        # Progress bar
        progress_bar = st.progress(0)
        completed_count = 0
        
        # Multi-threading
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(scrape_single_page, url): url for url in urls}
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result["status"] == "success":
                        status_containers[url].markdown(f"✅ **Done**: `{url}`")
                    else:
                        status_containers[url].markdown(f"❌ **Error**: `{url}` - {result.get('error_message')}")
                        
                except Exception as exc:
                    status_containers[url].markdown(f"❌ **Critical Error**: `{url}` - {exc}")
                
                completed_count += 1
                progress_bar.progress(completed_count / len(urls))
                
        st.success("Scraping completed!")
        
        # Bundling
        st.subheader("Knowledge Bundle")
        full_content = ""
        success_count = 0
        
        for res in results:
            if res["status"] == "success":
                full_content += res["content"]
                success_count += 1
                
        st.write(f"Bundled {success_count} pages successfully.")
        
        if full_content:
            st.text_area("Preview (First 1000 chars)", full_content[:1000] + "...", height=200)
            st.download_button(
                label="Download knowledge.md",
                data=full_content,
                file_name="knowledge.md",
                mime="text/markdown"
            )
        else:
            st.error("No content was retrieved.")
