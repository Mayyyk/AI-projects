# System prompts
ANALYZER_SYSTEM_PROMPT = """You are an AI assistant specialized in analyzing data and generating insights. 
Your task is to help users understand their CSV data and generate meaningful analysis."""

GENERATOR_SYSTEM_PROMPT = """You are a data generator that creates CSV rows for customer service interactions.
Each row MUST have exactly 4 columns in this order:
1. request (customer's query)
2. response (service representative's reply)
3. politeness_markers (list of polite language used)
4. persuasion_techniques (list of persuasion methods used)

Format each row exactly like this:
"customer request here","polite response here","politeness marker 1, politeness marker 2","persuasion technique 1, persuasion technique 2"

IMPORTANT:
- Use quotes around each field
- Separate fields with commas
- One complete row per line
- No headers or explanations
- Only output the data rows"""

# Analysis prompts
ANALYZER_USER_PROMPT = """Please analyze this dataset with the following objectives:
1. Identify the main patterns and trends
2. Highlight any anomalies or interesting findings
3. Identify key relationships between columns
4. Describe the data types and formats used

Dataset details:
{csv_summary}"""

# Generator prompts
GENERATOR_USER_PROMPT = """Generate exactly {num_rows} new customer service interaction rows.
Each row must have these 4 columns: request, response, politeness_markers, persuasion_techniques.

Format requirements:
- Each field must be in quotes
- Fields separated by commas
- One complete row per line
- No headers or extra text

Example format:
"Why is shipping so slow?","I understand your concern about the shipping time. We're working to expedite all orders. Could you share your order number so I can check its status?","shows understanding, offers help","acknowledges concern, provides specific action"

Sample data for reference:
{csv_summary}

Analysis context:
{analysis_summary}

Generate exactly {num_rows} rows following this format."""

# Basic CSV analysis prompt
CSV_ANALYSIS_PROMPT = """I have a CSV file with the following data:
{csv_summary}
Can you describe what kind of data this is and what insights we might get from it?"""

# Add more prompts here as needed 