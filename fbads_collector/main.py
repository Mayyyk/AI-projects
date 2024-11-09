import agentql
from playwright.sync_api import sync_playwright
from loguru import logger
from pathlib import Path
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from typing import List
import re
import time
from urllib.parse import unquote

# Configure logging
logger.add(
    "logs/facebook_ads_collector.log",
    rotation="1 day",
    retention="7 days",
    level="INFO"
)

class SearchParameters(BaseModel):
    """Pydantic model for validating search parameters"""
    keywords: List[str] = Field(..., min_items=1, max_items=5)
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, keywords):
        """Validate each keyword for length and characters"""
        for keyword in keywords:
            if not 2 <= len(keyword) <= 50:
                raise ValueError(f"Keyword '{keyword}' must be between 2 and 50 characters")
            if not re.match(r'^[a-zA-Z0-9\s\-]+$', keyword):
                raise ValueError(f"Keyword '{keyword}' contains invalid characters")
        return keywords

class FacebookAdsCollector:
    def __init__(self):
        """Initialize the Facebook Ads Collector"""
        self.search_params = None
        self.base_url = os.getenv('FB_ADS_LIBRARY_URL')
        
    def get_user_input(self) -> SearchParameters:
        """Get and validate search keywords from user input"""
        try:
            print("\n=== Facebook Ads Library Link Collector ===")
            print("Enter up to 5 keywords or phrases for your niche search.")
            print("Separate multiple keywords with commas.")
            print("Example: digital marketing, social media, advertising")
            
            user_input = input("\nEnter keywords: ").strip()
            keywords = [k.strip() for k in user_input.split(',') if k.strip()]
            
            # Validate input using Pydantic model
            self.search_params = SearchParameters(keywords=keywords)
            logger.info(f"Validated keywords: {self.search_params.keywords}")
            return self.search_params
            
        except ValueError as e:
            logger.error(f"Invalid input: {str(e)}")
            print(f"\nError: {str(e)}")
            print("Please try again with valid keywords.")
            return self.get_user_input()
        
        except Exception as e:
            logger.error(f"Unexpected error during input: {str(e)}")
            raise

    def extract_profile_links(self, page) -> List[str]:
        """Extract profile links from search results"""
        try:
            logger.info("Extracting profile links from search results...")
            
            # Wait for results to load
            time.sleep(5)
            
            # Fixed query syntax - removed attributes nesting
            ALL_LINKS_QUERY = """
            {
                links(selector: "a[href*='facebook.com']") {
                    href
                    text
                }
            }
            """
            
            profile_links = set()
            response = page.query_elements(ALL_LINKS_QUERY)
            
            # Updated response handling to match new query structure
            if hasattr(response, 'links') and response.links:
                for link in response.links:
                    try:
                        href = link.href  # Directly access href instead of attributes.href
                        if href and isinstance(href, str):
                            # Clean up redirect URL if needed
                            if "l.php?u=" in href:
                                clean_url = unquote(href.split('u=')[1].split('&')[0])
                                href = clean_url
                            
                            # Only keep Facebook profile links
                            if "facebook.com" in href and "/ads/library" not in href:
                                logger.info(f"Found company URL: {href}")
                                profile_links.add(href)
                    except Exception as e:
                        logger.error(f"Error processing link: {str(e)}")
                        continue
            else:
                logger.warning("No links found in the response")
            
            # Save links to file
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = f"results/profile_links_{timestamp}.txt"
            os.makedirs("results", exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for link in sorted(profile_links):
                    f.write(f"{link}\n")
            
            logger.info(f"Saved {len(profile_links)} unique profile links to {output_file}")
            return list(profile_links)
            
        except Exception as e:
            logger.error(f"Error extracting profile links: {str(e)}")
            page.screenshot(path=f"error_extraction_{time.strftime('%Y%m%d_%H%M%S')}.png")
            raise

    def search_ads_library(self, page) -> None:
        """Search Facebook Ads Library using AgentQL"""
        try:
            for keyword in self.search_params.keywords:
                logger.info(f"Searching for keyword: {keyword}")
                
                # Navigate to Facebook Ads Library
                page.goto(self.base_url)
                logger.info("Waiting for page to load completely...")
                page.wait_for_load_state("networkidle")
                time.sleep(3)
                
                # Handle country selection
                logger.info("Setting country to United States...")
                COUNTRY_QUERY = """
                {
                    country_search(input field to search for country or button to open country selection)
                }
                """
                
                response = page.query_elements(COUNTRY_QUERY)
                if response.country_search:
                    # Click to open country selection
                    response.country_search.click()
                    time.sleep(2)
                    
                    # Look for the search input
                    SEARCH_COUNTRY_QUERY = """
                    {
                        search_input(input field with placeholder "Search for country")
                    }
                    """
                    
                    search_response = page.query_elements(SEARCH_COUNTRY_QUERY)
                    if search_response.search_input:
                        search_response.search_input.fill("United States")
                        time.sleep(2)
                        
                        # Click United States option
                        US_OPTION_QUERY = """
                        {
                            us_option(clickable element containing exact text "United States")
                        }
                        """
                        
                        us_response = page.query_elements(US_OPTION_QUERY)
                        if us_response.us_option:
                            us_response.us_option.click()
                            time.sleep(2)
                
                # Handle ad category selection
                logger.info("Setting ad category...")
                AD_CATEGORY_QUERY = """
                {
                    category_button(button with text "Ad category" or button to select ad category)
                }
                """
                
                category_response = page.query_elements(AD_CATEGORY_QUERY)
                if category_response.category_button:
                    category_response.category_button.click()
                    time.sleep(2)
                    
                    # First clear any existing selection
                    CLEAR_CATEGORY_QUERY = """
                    {
                        clear_button(button to clear or remove current category selection)
                    }
                    """
                    try:
                        clear_response = page.query_elements(CLEAR_CATEGORY_QUERY)
                        if clear_response.clear_button:
                            clear_response.clear_button.click()
                            time.sleep(1)
                    except:
                        pass
                    
                    # Select "All ads" option with more specific query
                    ALL_ADS_QUERY = """
                    {
                        all_ads_option(element with text "All Ads" in the category dropdown menu)
                    }
                    """
                    
                    all_ads_response = page.query_elements(ALL_ADS_QUERY)
                    if all_ads_response.all_ads_option:
                        all_ads_response.all_ads_option.click()
                        time.sleep(2)
                
                # Handle search input
                logger.info(f"Searching for keyword: {keyword}")
                SEARCH_QUERY = """
                {
                    search_input(input field for searching ads or input with placeholder containing "search")
                }
                """
                
                search_response = page.query_elements(SEARCH_QUERY)
                if search_response.search_input:
                    search_response.search_input.fill(keyword)
                    time.sleep(1)
                    page.keyboard.press("Enter")
                    logger.info(f"Entered search term: {keyword}")
                    
                    # Wait for results to load
                    time.sleep(5)
                    
                    # Extract profile links
                    profile_links = self.extract_profile_links(page)
                    logger.info(f"Found {len(profile_links)} unique profile links for keyword: {keyword}")
                    
                    # Save screenshot for debugging
                    page.screenshot(path=f"search_results_{keyword.replace(' ', '_')}.png")
                    logger.info(f"Saved screenshot for: {keyword}")
                
        except Exception as e:
            logger.error(f"Error during ads library search: {str(e)}")
            page.screenshot(path=f"error_{time.strftime('%Y%m%d_%H%M%S')}.png")
            raise

def main():
    """Main entry point of the script"""
    try:
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize the collector
        collector = FacebookAdsCollector()
        logger.info("Facebook Ads Collector initialized successfully")
        
        # Get search parameters from user
        search_params = collector.get_user_input()
        logger.info(f"Starting search with parameters: {search_params.keywords}")
        
        # Initialize browser and perform search
        with sync_playwright() as playwright:
            # Configure browser with English locale and full screen
            browser = playwright.chromium.launch(
                headless=False,
                args=[
                    '--lang=en-US',
                    '--accept-lang=en-US,en',
                    '--start-maximized'  # Start browser maximized
                ]
            )
            # Create context with full screen viewport
            context = browser.new_context(
                locale='en-US',
                timezone_id='America/New_York',
                viewport=None  # This will use the full screen size
            )
            page = agentql.wrap(context.new_page())
            
            # Ensure the page is maximized
            page.set_viewport_size({"width": 1920, "height": 1080})  # Full HD size
            page.evaluate("document.documentElement.requestFullscreen()")
            
            # Set language headers directly on the page
            page.set_extra_http_headers({
                'Accept-Language': 'en-US,en;q=0.9'
            })
            
            # Perform the search
            collector.search_ads_library(page)
            
            # Close the browser
            browser.close()
        
    except Exception as e:
        logger.error(f"Failed to initialize the application: {str(e)}")
        raise

if __name__ == "__main__":
    main()
