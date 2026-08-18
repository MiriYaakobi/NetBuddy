import os
import json
import time
import logging
import ipaddress
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from bidi.algorithm import get_display

# --- Verbose Toggle ---
# True = Show all internal steps (agent thoughts, tool executions). 
# False = Quiet mode, only show the final answer to the user.
VERBOSE_MODE = True

# Configure logging dynamically based on the VERBOSE_MODE flag
log_level = logging.INFO if VERBOSE_MODE else logging.WARNING
logging.basicConfig(level=log_level, format="%(asctime)s %(message)s")
log = logging.getLogger("agent")

# Load secrets from the .env file into environment variables
load_dotenv()

# Initialize the OpenAI client pointing to Google's Gemini API endpoint
client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
)

# Define the specific model version to use
MODEL = "gemini-3-flash-preview"


def search_course_notes(topic: str) -> str:
    """Returns summarized notes for a given Computer Communications topic."""
    # Mock database representing personal course notes
    fake_notes = {
        "subnetting": "חישוב Subnetting נועד לחלק רשת גדולה לתתי-רשתות קטנות.",
        "tcp": "פרוטוקול TCP מבטיח אמינות בהעברת נתונים בעזרת לחיצת יד משולשת.",
        "vlans": "VLANs (Virtual LANs) מאפשרים חלוקה לוגית של רשת פיזית אחת למספר רשתות נפרדות.",
        "stp": "פרוטוקול Spanning Tree Protocol (STP) מונע לולאות (loops) ברשתות של מתגים."
    }
    return fake_notes.get(topic.lower(), f"לא מצאתי סיכומים על הנושא: {topic}")


def calculate_subnet(cidr: str) -> str:
    """Calculates network details for a given CIDR block."""
    try:
        # Create a network object; strict=False allows host IPs with subnet masks
        network = ipaddress.IPv4Network(cidr, strict=False)
        
        # Calculate usable hosts (excluding network and broadcast addresses)
        usable_hosts = network.num_addresses - 2 if network.num_addresses > 2 else 0
        
        return (f"Network Address: {network.network_address}, "
                f"Broadcast Address: {network.broadcast_address}, "
                f"Usable Hosts: {usable_hosts}, "
                f"Netmask: {network.netmask}")
    except ValueError as e:
        return f"Error: Invalid CIDR format. Details: {e}"


# Define all tools available to the LLM using JSON Schema format
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_course_notes",
            "description": "Searches the Computer Communications course notes. Use this tool when the user asks questions about the study material to retrieve accurate facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The networking topic to search for in English (e.g., subnetting, tcp)"}
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_subnet",
            "description": "Calculates network data (Subnetting) based on an IP address and CIDR prefix. Use this tool when the user asks to calculate a network address, broadcast, or number of usable hosts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cidr": {"type": "string", "description": "The IP address with CIDR notation, e.g., '10.0.0.0/16' or '192.168.1.5/24'"}
                },
                "required": ["cidr"],
            },
        },
    }
]

# Map the tool names (strings) to the actual Python functions
available_tools = {
    "search_course_notes": search_course_notes,
    "calculate_subnet": calculate_subnet
}


def call_with_retry(messages, tools, max_retries=4):
    """Calls the LLM API with exponential backoff to handle rate limits."""
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=MODEL, 
                messages=messages, 
                tools=tools,
                temperature=0  # Deterministic output for agent logic
            )
        except RateLimitError:
            wait = 2 ** attempt  # Exponentially increase wait time: 1, 2, 4, 8 seconds
            log.warning(f"Rate limit reached, waiting {wait} seconds...")
            time.sleep(wait)
    raise RuntimeError("Failed after all retry attempts due to Rate Limits.")


def run_agent(user_message: str, max_steps: int = 5) -> str:
    """Runs the main agent loop (ReAct pattern), handling tool calls and responses."""
    
    # Initialize conversation history with the system prompt and the user's query
    messages = [
        {"role": "system", "content": "אתה עוזר לימודים אישי לקורס תקשורת מחשבים. ענה בעברית. חובה עליך להשתמש בכלים כדי לחפש בסיכומים לפני שאתה עונה. אם אין מספיק מידע בסיכומים, אמור זאת מפורשות במקום להמציא נתונים."},
        {"role": "user", "content": user_message},
    ]

    # Initialize tracking variables for token usage
    total_prompt_tokens = 0
    total_completion_tokens = 0

    # Agent Loop: limit iterations to prevent infinite runaway loops
    for step in range(max_steps):
        log.info(f"--- Agent is thinking (Step {step + 1}) ---") 
        
        response = call_with_retry(messages, tools)
        
        # Accumulate token usage from the current API response
        if response.usage:
            total_prompt_tokens += response.usage.prompt_tokens
            total_completion_tokens += response.usage.completion_tokens
        
        msg = response.choices[0].message
        messages.append(msg) 

        # Decision Point: Did the model request any tools?
        if not msg.tool_calls:
            
            # Live Cost Calculation based on estimated Gemini Flash pricing
            # ($0.075 per 1M prompt tokens, $0.30 per 1M completion tokens)
            prompt_cost = (total_prompt_tokens / 1_000_000) * 0.075
            comp_cost = (total_completion_tokens / 1_000_000) * 0.30
            total_cost_usd = prompt_cost + comp_cost
            
            log.info(f"Total Tokens -> Prompt: {total_prompt_tokens}, Completion: {total_completion_tokens}")
            log.info(f"Estimated Cost -> ${total_cost_usd:.6f} USD")
            
            # No tool requested means the agent has reached a final answer
            return msg.content

        # Execute all tools requested by the model
        for call in msg.tool_calls:
            fn = available_tools[call.function.name]
            args = json.loads(call.function.arguments) 
            
            log.info(f"Executing tool: {call.function.name} | parameters: {args}")
            
            try:
                result = fn(**args) 
            except Exception as e:
                result = f"Error executing tool: {e}"
            
            log.info(f"Tool result: {str(result)[:100]}")
            
            # Append the tool's result back to the conversation history
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})

    return "הגעתי למקסימום הצעדים בלי תשובה סופית."


if __name__ == "__main__":
    # Test the agent with a complex networking question
    answer = run_agent("היי! תוכל לחשב לי כמה כתובות מארחים (hosts) חוקיות יש ברשת 192.168.5.0/26, ומה כתובת ה-Broadcast שלה?")
    
    # Fix Hebrew RTL display rendering in the terminal
    print(get_display(answer))