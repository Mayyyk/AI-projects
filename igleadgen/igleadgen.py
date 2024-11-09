from tavily import TavilyClient
import os
from dotenv import load_dotenv
import json
from datetime import datetime

def test_connection(client: TavilyClient) -> bool:
    """Test the API connection and authentication"""
    try:
        client.search("test query")
        print("✅ API connection successful!")
        return True
            
    except Exception as e:
        print(f"❌ Error testing connection: {str(e)}")
        return False

def search_instagram_leads(client: TavilyClient, niche: str, location: str) -> dict:
    """
    Search for Instagram business leads based on niche and location
    
    Args:
        client: TavilyClient instance
        niche: Business niche/industry (e.g., 'coffee shop', 'yoga studio')
        location: Geographic location (e.g., 'Miami, FL')
        
    Returns:
        dict: Search results from Tavily API
    """
    try:
        # Format search query to target Instagram business accounts
        query = f"instagram {niche} business in {location}"
        
        # Make API call with specific search parameters
        response = client.search(
            query=query,
            search_depth="advanced",  # More comprehensive search
            include_answer=True,      # Get AI-generated summary
            include_domains=["instagram.com", "facebook.com", "linkedin.com"],
            max_results=50  # Increase the number of results
        )
        
        print(f"✅ Found results for {niche} businesses in {location}")
        return response
        
    except Exception as e:
        print(f"❌ Search error: {str(e)}")
        return None

def process_leads(results: dict, search_niche: str, search_location: str, minimal: bool) -> list[dict]:
    """
    Process and structure the raw search results into clean lead data
    
    Args:
        results: Raw response from Tavily API
        search_niche: Original niche input from user
        search_location: Original location input from user
        minimal: Whether to store only the profile URL
        
    Returns:
        list[dict]: List of processed and validated leads
    """
    processed_leads = []
    
    for result in results.get('results', []):
        # Skip if no URL or not Instagram
        if not result.get('url') or 'instagram.com' not in result.get('url'):
            continue
            
        # Extract Instagram handle from URL
        handle = result.get('url').split('instagram.com/')[-1].strip('/')
        
        # Basic validation
        if not handle or handle == "p":  # Skip if no handle or it's a post URL
            continue
            
        lead = {
            "profile_url": result.get('url')
        }
        
        if not minimal:
            # Extract business info
            title = result.get('title', '').split('•')[0].strip()  # Clean title before bullet point
            content = result.get('content', '')
            
            lead.update({
                "instagram_handle": handle,
                "business_name": title,
                "description": content,
                "relevance_score": result.get('score', 0),
                "niche": search_niche,
                "location": search_location
            })
        
        processed_leads.append(lead)
    
    return processed_leads

def save_leads(leads: list[dict], filename: str = "instagram_leads.json", minimal: bool = False) -> int:
    """
    Save leads to a JSON file, appending new results to existing data
    
    Args:
        leads: List of processed lead dictionaries
        filename: Name of the JSON file to save to
        minimal: Whether to store only the profile URL
    """
    # Add timestamp to each lead
    timestamp = datetime.now().isoformat()
    for lead in leads:
        lead['found_at'] = timestamp
    
    # Load existing data if file exists
    existing_leads = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_leads = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Error reading existing file. Starting fresh.")
    
    # Check for duplicates using Instagram handle
    existing_handles = {lead['instagram_handle'] for lead in existing_leads if 'instagram_handle' in lead}
    new_leads = [lead for lead in leads if lead.get('instagram_handle') not in existing_handles]
    
    # Combine existing and new leads
    all_leads = existing_leads + new_leads
    
    # Sort all leads by relevance score (highest first) if not minimal
    if not minimal:
        all_leads = sorted(
            all_leads,
            key=lambda x: float(x.get('relevance_score', 0)),
            reverse=True
        )
    
    # If minimal, filter to only include profile URLs and add numbering
    if minimal:
        all_leads = [{"number": idx + 1, "profile_url": lead["profile_url"]} for idx, lead in enumerate(all_leads)]
    
    # Save updated data
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_leads, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(new_leads)} new leads to {filename}")
        print(f"📊 Total leads in database: {len(all_leads)}")
        return len(new_leads)
    except Exception as e:
        print(f"❌ Error saving leads: {str(e)}")
        return 0

if __name__ == "__main__":
    try:
        # Initialize client
        load_dotenv()
        api_key = os.getenv('TAVILY_API_KEY')
        
        if not api_key:
            raise ValueError("Tavily API key not found in environment variables")
            
        client = TavilyClient(api_key=api_key)
        
        # Test connection
        if test_connection(client):
            # Get user input
            print("\n=== Instagram Lead Generator ===")
            niche = input("Enter business niche (e.g., coffee shop, yoga studio): ").strip()
            location = input("Enter location (e.g., Miami, FL): ").strip()
            minimal = input("Do you want to store only profile URLs? (yes/no): ").strip().lower() == 'yes'
            
            if not niche or not location:
                raise ValueError("Niche and location cannot be empty")
            
            # Initialize variables for loop
            total_new_leads = 0
            iteration = 0
            
            while True:
                iteration += 1
                print(f"\n=== Query Iteration {iteration} ===")
                
                # Search with user input
                results = search_instagram_leads(
                    client=client,
                    niche=niche,
                    location=location
                )
                
                if results:
                    leads = process_leads(
                        results=results,
                        search_niche=niche,
                        search_location=location,
                        minimal=minimal
                    )
                    
                    # Save leads to file and get the number of new leads
                    new_leads_count = save_leads(leads, minimal=minimal)
                    total_new_leads += new_leads_count
                    
                    # Break the loop if no new leads are found
                    if new_leads_count == 0:
                        print("\nNo new leads found. Stopping the query loop.")
                        break
                else:
                    print("\nNo results returned from the API. Stopping the query loop.")
                    break
            
            print(f"\nTotal new leads found: {total_new_leads}")
                
    except Exception as e:
        print(f"Error: {str(e)}")
