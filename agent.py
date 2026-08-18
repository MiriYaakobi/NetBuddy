import os
import json
import time
import logging
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from bidi.algorithm import get_display

# 1. Setup Observability (Logging)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("agent")

load_dotenv()

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
)

MODEL = "gemini-3-flash-preview"


def search_course_notes(topic: str) -> str:
    """Returns summarized notes for a given Computer Communications topic."""
    fake_notes = {
        "subnetting": "חישוב Subnetting נועד לחלק רשת גדולה לתתי-רשתות קטנות.",
        "tcp": "פרוטוקול TCP מבטיח אמינות בהעברת נתונים בעזרת לחיצת יד משולשת.",
        "vlans": "VLANs (Virtual LANs) מאפשרים חלוקה לוגית של רשת פיזית אחת למספר רשתות נפרדות.",
        "stp": "פרוטוקול Spanning Tree Protocol (STP) מונע לולאות (loops) ברשתות של מתגים."
    }
    return fake_notes.get(topic.lower(), f"לא מצאתי סיכומים על הנושא: {topic}")


tools = [{
    "type": "function",
    "function": {
        "name": "search_course_notes",
        "description": "מחפש בסיכומי הקורס בתקשורת מחשבים. השתמש בכלי זה כשהמשתמש שואל שאלות על חומר הלימוד כדי להביא עובדות מדויקות.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "The networking topic to search for in English (e.g., subnetting, tcp)"}
            },
            "required": ["topic"],
        },
    },
}]

available_tools = {"search_course_notes": search_course_notes}

# 2. Add Rate Limit Handling (Exponential Backoff)
def call_with_retry(messages, tools, max_retries=4):
    """Calls the LLM API with exponential backoff for rate limits."""
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model=MODEL, 
                messages=messages, 
                tools=tools,
                temperature=0
            )
        except RateLimitError:
            wait = 2 ** attempt  # 1, 2, 4, 8 seconds
            log.warning(f"Rate limit reached, waiting {wait} seconds...")
            time.sleep(wait)
    raise RuntimeError("Failed after all retry attempts due to Rate Limits.")


def run_agent(user_message: str, max_steps: int = 5) -> str:
    """Runs the main agent loop, handling tool calls and responses."""
    
    messages = [
        {"role": "system", "content": "אתה עוזר לימודים אישי לקורס תקשורת מחשבים. ענה בעברית. חובה עליך להשתמש בכלים כדי לחפש בסיכומים לפני שאתה עונה. אם אין מספיק מידע בסיכומים, אמור זאת מפורשות במקום להמציא נתונים."},
        {"role": "user", "content": user_message},
    ]

    # 3. Initialize Token Tracking Variables
    total_prompt_tokens = 0
    total_completion_tokens = 0

    for step in range(max_steps):
        log.info(f"--- Agent is thinking (Step {step + 1}) ---") 
        
        # Use our new retry function instead of calling client directly
        response = call_with_retry(messages, tools)
        
        # Track Tokens
        if response.usage:
            total_prompt_tokens += response.usage.prompt_tokens
            total_completion_tokens += response.usage.completion_tokens
        
        msg = response.choices[0].message
        messages.append(msg) 

        if not msg.tool_calls:
            # Print Final Token Usage before returning
            log.info(f"Total Tokens Used -> Prompt: {total_prompt_tokens}, Completion: {total_completion_tokens}, Total: {total_prompt_tokens + total_completion_tokens}")
            return msg.content

        for call in msg.tool_calls:
            fn = available_tools[call.function.name]
            args = json.loads(call.function.arguments) 
            
            # Upgraded Observability logging
            log.info(f"Executing tool: {call.function.name} | parameters: {args}")
            
            try:
                result = fn(**args) 
            except Exception as e:
                result = f"Error executing tool: {e}"
            
            # Log the result
            log.info(f"Tool result: {str(result)[:100]}")
            
            messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})

    return "הגעתי למקסימום הצעדים בלי תשובה סופית."


if __name__ == "__main__":
    answer = run_agent("היי! מה התפקיד של פרוטוקול TCP לפי הסיכומים שלי?")
    print(get_display(answer))