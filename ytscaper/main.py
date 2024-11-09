import os
import logging
import agentql
from threading import Timer
from openai import OpenAI
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Initialize OpenAI client
XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)


# Define AgentQL query for YouTube videos
VIDEO_QUERY = """
{
    videos[] {
        video_title
        views
        upload_date
    }
}
"""

# Scrape YouTube data
def scrape_youtube_channel(channel_url):
    print(f"\nStarting to scrape: {channel_url}")
    with sync_playwright() as playwright, playwright.chromium.launch(headless=False) as browser:
        print("Browser launched")
        page = agentql.wrap(browser.new_page())
        print("Navigating to page...")
        page.goto(channel_url)
        
        print("Waiting for page to load...")
        # Wait for content to load
        page.wait_for_page_ready_state()
        
        # Get video data
        print("Executing AgentQL query...")
        response = page.query_data(VIDEO_QUERY)
        videos = response.get('videos', [])
        
        # Extract just the number from views, regardless of language
        def extract_views(view_string):
            if not view_string:
                return 0
                
            # Clean up the input string
            view_string = view_string.strip().upper()
            
            # Define multipliers for different suffixes
            multipliers = {
                'K': 1000,
                'M': 1000000,
                'B': 1000000000,
                'tys.': 1000,  # Polish thousand
                'mln': 1000000,  # Polish million
                'mld': 1000000000,  # Polish billion
            }
            
            try:
                # Remove any spaces within the number
                view_string = ''.join(view_string.split())
                
                # Extract the numeric part
                numeric_part = ''
                for char in view_string:
                    if char.isdigit() or char == '.' or char == ',':
                        numeric_part += char
                    else:
                        break
                
                # Replace comma with dot for decimal point
                numeric_part = numeric_part.replace(',', '.')
                
                # Convert to float
                number = float(numeric_part)
                
                # Check for multiplier suffixes
                for suffix, multiplier in multipliers.items():
                    if suffix in view_string:
                        return int(number * multiplier)
                
                # If no multiplier found, return the number as is
                return int(number)
                
            except (ValueError, TypeError):
                log.warning(f"Could not parse view count: {view_string}")
                return 0
        
        # Sort videos by views
        sorted_videos = sorted(
            videos,
            key=lambda x: extract_views(x['views']),
            reverse=True
        )
        
        print(f"Query complete. Found {len(videos)} videos")
        return sorted_videos[:10]  # Return top 10 videos

# Main execution
if __name__ == "__main__":
    print("Script started")
    
    # Scrape YouTube data
    channel_url = "https://www.youtube.com/@MichalMidor/videos"
    print("\nStarting YouTube scrape...")
    top_videos = scrape_youtube_channel(channel_url)
    
    print("\nFormatting results...")
    # Format video data for Grok
    video_summary = "\n".join([
        f"Title: {video['video_title']}, Views: {video['views']}, Upload Date: {video['upload_date']}"
        for video in top_videos  # No need to slice, we already have top 10
    ])
    
    print("\nTop 10 Most Viewed Videos:")
    print(video_summary)
    
    # Store the raw AgentQL data for Grok
    raw_data = {
        "channel_url": channel_url,
        "video_count": len(top_videos),
        "videos": top_videos
    }
    
    # Create Grok API prompts
    system_prompt = """You are an AI assistant specializing in YouTube channel analysis and data formatting. 
Your expertise includes:
- Analyzing YouTube channel metrics and trends
- Formatting raw data into clean, readable markdown
- Identifying patterns in video performance
- Providing insights about content strategy

Please format your response in clean markdown, using appropriate headers, lists, and tables where relevant."""

    user_prompt = f"""I've scraped data from a YouTube channel. Here's the raw data:

Channel URL: {raw_data['channel_url']}
Total Videos Analyzed: {raw_data['video_count']}

Raw video data:
{video_summary}

Please:
1. Format this data into a clean, readable markdown report
2. Analyze the view counts and upload patterns
3. Identify any trends or patterns in the video titles
4. Provide insights about what types of content perform best
5. Include a summary table of the top performing videos

Format the response in markdown with clear sections."""

    # Call Grok API
    completion = client.chat.completions.create(
        model="grok-beta",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    
    # Get Grok's response
    grok_analysis = completion.choices[0].message.content
    
    # Print to console
    print("\nGrok's Analysis:")
    print(grok_analysis)
    
    # Save to markdown file
    output_filename = "youtube_analysis.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("# YouTube Channel Analysis\n\n")
        f.write(f"Analysis generated for: {channel_url}\n\n")
        f.write("---\n\n")
        f.write(grok_analysis)
    
    print(f"\nAnalysis saved to {output_filename}")

