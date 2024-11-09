from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from typing import List, Dict
import datetime
import asyncio
import aiohttp
from code_tracker import CodeChangeTracker, update_progress_file

# Load environment variables
load_dotenv()
print("Environment variables loaded...")

# Initialize clients
openai_client = OpenAI()
perplexity_client = OpenAI(
    api_key=os.getenv("PERPLEXITY_API_KEY"),
    base_url="https://api.perplexity.ai"
)
print("API clients initialized...")

def choose_mode() -> str:
    """Choose between fast mode (smaller model) or quality mode (larger model)"""
    print("\nAvailable modes:")
    print("1. Quality mode (default) - Uses more powerful model for better results")
    print("2. Fast mode - Uses lighter model for quicker results")
    
    choice = input("\nDo you want to run in fast mode? (y/n): ").lower()
    
    if choice == 'y':
        print("✓ Fast mode selected - Using llama-3.1-sonar-small-128k-online")
        return "llama-3.1-sonar-small-128k-online"
    else:
        print("✓ Quality mode selected - Using llama-3.1-sonar-large-128k-online")
        return "llama-3.1-sonar-large-128k-online"

def generate_research_queries(user_input: str) -> Dict:
    """First agent: Generates research queries based on user input"""
    print(f"\n1. Generating research queries for: '{user_input}'")
    
    prompt = f"""
    You are a research query generator. Your task is to deeply analyze the user's query to understand their core research needs and generate targeted search queries.
    If it makes sense, use your own knowledge to improve prompts - if you know it's smart to research something more than the user asked, do it.

    1. First, identify the main topics, subtopics, and any specific aspects mentioned in the query
    2. Consider different angles, perspectives, and related areas that would provide comprehensive research coverage
    3. Generate search queries that:
        - Must be highly specific and distinct from each other
        - Approach the topic from radically different angles and perspectives
        - Use precise technical terminology and domain-specific language
        - Target niche subtopics and specialized aspects
        - Include contrasting viewpoints and alternative interpretations
        - Focus on unique case studies and specific examples
        - Examine interconnections with other fields/domains
        - Look for cutting-edge research and emerging trends
        - Seek expert analysis and authoritative sources
        - Consider historical context and future implications

    Return a JSON object with this structure:
    {{
        "user_prompt": "Original user query",
        "topic_analysis": "Your detailed analysis of main topics and diverse research angles",
        "search_queries": [
            "Array of 10 highly distinct and specific search queries, each exploring a unique aspect or perspective of the topic"
        ]
    }}
    
    User Query: {user_input}
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": prompt}],
        response_format={ "type": "json_object" }
    )
    
    result = json.loads(response.choices[0].message.content)
    
    # Print the reasoning/analysis first
    print("\n✓ Topic Analysis:")
    print(f"{result['topic_analysis']}")
    
    # Then print the queries
    print("\n✓ Generated research queries:")
    for i, query in enumerate(result['search_queries'], 1):
        print(f"   {i}. {query}")
    
    return result

async def perform_single_search(session, query: str, i: int, model: str) -> Dict:
    """Perform a single search query"""
    try:
        async with session.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a highly analytical research assistant focused on evidence-based findings. "
                            "Your task is to:\n"
                            "1. Deeply analyze the query to understand the core research needs\n"
                            "2. Provide strictly factual information supported by reliable sources\n"
                            "3. Focus on recent, peer-reviewed research and authoritative sources\n"
                            "4. Draw precise conclusions that directly address the query context\n"
                            "5. Prioritize accuracy and relevance over breadth\n"
                            "6. Cite specific studies, papers, or expert sources where possible\n"
                            "7. Highlight any important caveats or limitations in the findings\n\n"
                            "Ensure your response is concise, well-structured, and directly addresses "
                            "the key aspects of the query while maintaining strict factual accuracy."
                        ),
                    },
                    {
                        "role": "user",
                        "content": query,
                    },
                ]
            }
        ) as response:
            result = await response.json()
            return {
                "query": query,
                "response": result['choices'][0]['message']['content']
            }
    except Exception as e:
        print(f"\n   ✗ Error in search {i}: {str(e)}")
        return {
            "query": query,
            "response": f"Error: {str(e)}"
        }

async def perform_web_searches_async(queries: List[str], model: str) -> List[Dict]:
    """Performs web searches using Perplexity API concurrently"""
    print("\n2. Performing web searches concurrently...")
    total_queries = len(queries)
    completed_queries = 0
    
    async def search_with_progress(session, query: str, i: int) -> Dict:
        nonlocal completed_queries
        print(f"\r   Progress: {completed_queries}/{total_queries} queries completed ({(completed_queries/total_queries)*100:.1f}%)", end="")
        
        result = await perform_single_search(session, query, i, model)
        
        completed_queries += 1
        print(f"\r   Progress: {completed_queries}/{total_queries} queries completed ({(completed_queries/total_queries)*100:.1f}%)", end="")
        return result
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            search_with_progress(session, query, i+1) 
            for i, query in enumerate(queries)
        ]
        results = await asyncio.gather(*tasks)
    
    print("\n   ✓ All searches completed")
    return results

def perform_web_searches(queries: List[str], model: str) -> List[Dict]:
    """Wrapper function to run async searches"""
    return asyncio.run(perform_web_searches_async(queries, model))

def synthesize_research(original_prompt: str, search_results: List[Dict]) -> str:
    """Second agent: Synthesizes all research into a final answer"""
    print("\n3. Synthesizing research findings...")
    
    synthesis_prompt = f"""
    Original user query: {original_prompt}
    
    Research findings:
    {json.dumps(search_results, indent=2)}
    
    Please analyze these findings deeply and synthesize them into a clear, engaging answer that directly addresses the user's needs:

    1. Focus only on information that is most relevant to the user's original query
    2. Present complex concepts in simple, easy-to-understand language
    3. Structure the response in a captivating way that maintains reader interest
    4. Highlight key insights and practical takeaways
    5. Omit any information that doesn't directly help answer the user's question
    6. Use clear examples and analogies where helpful
    7. Write in an engaging, conversational tone while maintaining accuracy

    In addition to synthesizing the research findings, please provide:
    - A brief summary of the main points and key takeaways
    - Simple, actionable advice on what the user should do next with this information
    - Bullet points or lists where appropriate to improve readability

    Your response should be captivating yet concise - make complex ideas crystal clear while keeping readers hooked from start to finish. Write like you're telling a fascinating story, not delivering a dry lecture. Make the output more concrete with detailed action steps when it makes sense.

    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": synthesis_prompt}]
    )
    
    print("✓ Research synthesis completed")
    return response.choices[0].message.content

def get_next_file_number():
    """Get the next available file number by checking existing files"""
    os.makedirs("research_results", exist_ok=True)
    existing_files = os.listdir("research_results")
    numbers = [int(f.split('_')[1].split('.')[0]) for f in existing_files 
              if f.startswith('research_') and f.endswith('.md')]
    return max(numbers, default=0) + 1

def save_to_markdown(user_input: str, result: str, research_plan: Dict, execution_time: float):
    """Save research results to a markdown file with sequential numbering"""
    # Get next available number
    file_number = get_next_file_number()
    
    # Create filename with just the number
    filename = f"research_{file_number:04d}.md"
    filepath = os.path.join("research_results", filename)
    
    # Get simplified prompt from research plan
    simplified_prompt = research_plan.get('topic_analysis', 'Topic analysis not available')
    
    # Format the markdown content
    content = f"""# Research #{file_number}

## Timestamp
{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Execution Time
{execution_time:.2f} seconds

## Original Query
{user_input}

## Topic Analysis
{simplified_prompt}

## Findings
{result}
"""
    
    # Save the file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\n✓ Results saved to {filepath}")

def research(user_input: str) -> tuple[str, Dict, float]:
    """Main research pipeline"""
    start_time = datetime.datetime.now()
    print("\n=== Starting Research Process ===")
    
    # Choose mode at the start
    model = choose_mode()
    
    # Step 1: Generate queries
    research_plan = generate_research_queries(user_input)
    print("Research queries generated...")
    
    # Step 2: Perform web searches with selected model
    search_results = perform_web_searches(research_plan['search_queries'], model)
    print("Web searches completed...")
    
    # Step 3: Synthesize final answer
    final_answer = synthesize_research(user_input, search_results)
    print("Research synthesis completed...")
    
    # Calculate execution time
    execution_time = (datetime.datetime.now() - start_time).total_seconds()
    
    print("\n=== Research Process Completed ===")
    print(f"Total execution time: {execution_time:.2f} seconds")
    
    return final_answer, research_plan, execution_time

if __name__ == "__main__":
    # Track code changes
    tracker = CodeChangeTracker()
    
    # Analyze changes (no need to save version separately anymore)
    changes = tracker.analyze_changes()
    
    # Update progress file if there are changes
    if changes and changes not in ["No changes detected", "Initial state saved"]:
        update_progress_file(changes)
    
    # Rest of your main code...
    user_input = input("\nEnter your research question: ")
    print("\nFinal Result:")
    print("-" * 50)
    result, research_plan, execution_time = research(user_input)
    print(result)
    
    # Save to markdown file
    save_to_markdown(user_input, result, research_plan, execution_time)
