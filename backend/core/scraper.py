import aiohttp
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

async def scrape_url(url: str) -> dict:
    """
    Scrapes a given business URL to extract the title, meta description, and main text content.
    """
    logger.info(f"Scraping URL: {url}")
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        
        # Extract title
        title = soup.title.string if soup.title else ""
        
        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and "content" in meta_tag.attrs:
            meta_desc = meta_tag["content"]

        # Extract logo (og:image, icon, or generic logo)
        logos = []
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            logos.append(og_image.get("content"))
            
        icons = soup.find_all("link", rel=lambda x: x and 'icon' in x.lower())
        for icon in icons:
            if icon.get("href"):
                logos.append(icon.get("href"))

        # Scrape Images (src and alt)
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            alt = img.get("alt", "")
            if src:
                images.append({"src": src, "alt": alt})
                if len(images) >= 10:
                    break
                    
        # Scrape Color Theme
        theme_colors = []
        meta_theme = soup.find("meta", attrs={"name": "theme-color"})
        if meta_theme and meta_theme.get("content"):
            theme_colors.append(meta_theme.get("content"))

        # Extract visible text (basic attempt)
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        text = soup.get_text(separator=" ", strip=True)
        # Limit text length to avoid token limits for basic scraping
        text = text[:5000]

        return {
            "url": url,
            "title": title.strip(),
            "description": meta_desc.strip(),
            "content": text,
            "logos": logos,
            "images": images,
            "theme_colors": theme_colors
        }
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return {
            "title": "Unknown",
            "description": "Failed to scrape description",
            "content": f"Failed to scrape content due to error: {e}",
            "logos": [],
            "images": [],
            "theme_colors": []
        }
