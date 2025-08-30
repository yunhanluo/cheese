from openai import AsyncOpenAI, RateLimitError, APIError, APITimeoutError

from dotenv import load_dotenv
import os

import asyncio
import json

from prompts import message_prompt, conversation_prompt, response_prompt


load_dotenv()

message_schema = {
    "name": "single_message",
    "schema": {
        "type": "object",
        "properties": {
            "points": {"type": "integer"},
            "sender": {"type": "integer"},
            "reasoning": {"type": "string"},
        },
        "required": ["sender", "text", "reasoning"],
        "additionalProperties": False
    },
}

response_schema = {
    "name": "ai_response",
    "schema": {
        "type": "object",
        "properties": {
             "data": {"type": "string"},
             "sender": {"type": "integer"},
             "priority": {"type": "integer"},
        },
        "required": ["data", "sender", "priority"],
        "additionalProperties": False
    },
}

conversation_schema = {
    "name": "conversation",
    "schema": {
        "type": "object",
        "properties": {
            "messages": {
                "type": "array",
                "items": message_schema['schema']
            }
        },
        "required": ["messages"],
        "additionalProperties": False
    }
}

match_schema = {
        "message_prompt": message_schema,
        "conversation_prompt": conversation_schema,
        "response_prompt": response_schema
    }

match_prompt = {
    "message_prompt": message_prompt,
    "conversation_prompt": conversation_prompt,
    "response_prompt": response_prompt
}


client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
semaphore = asyncio.Semaphore(15)

async def eval_text_points(text, prompt):
    
    backoff = 0.1
    txt = {"role": "user", "content": f"{text}"}
    
    for attempt in range(3): 
        try:
            async with semaphore:
                resp = await client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[match_prompt[prompt], txt],
                    response_format={
                        "type": "json_schema",
                        "json_schema": match_schema[prompt]
                    }
                )
                data = resp.choices[0].message.content
                return data
        except (RateLimitError, APIError, APITimeoutError) as e:
            print(f"API error on attempt {attempt + 1}: {type(e).__name__}")
            if attempt == 2:
                raise Exception(f"Failed to get response after 3 attempts. Last error: {str(e)}")
                
            await asyncio.sleep(backoff) 
            backoff = backoff ** attempt
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}")

async def main():
    text = [
    {'sender': 1234567899, 'data': 'I am racist.'},
    {'sender': 1234567899, 'data': 'I like to eat meat.'},
    {'sender': 1234567892, 'data': 'Hey! That is not cool. Knock it off.'},
    {'sender': 1234567894, 'data': 'A cheerful snail wearing sunglasses joyfully shared ideas about quantum physics with a vending machine in the middle of a brightly lit bowling alley.'},
     # Sample Data. Data should follow this format.
]
 
    try:
        result = await eval_text_points(text, "message_prompt")
        print(result)
    

        result2 = await eval_text_points(text, "conversation_prompt")
        print(result2)

        result3 = await eval_text_points(text, "response_prompt")
        print(result3)


    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
