from openai import AsyncOpenAI, RateLimitError, APIError, APITimeoutError
from typing import Dict, Any, List

from dotenv import load_dotenv
import os

import asyncio
import json
import random

from prompts import message_prompt, conversation_prompt


load_dotenv()

message_schema = {
    "name": "single_message",
    "schema": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "text": {"type": "string"},
            "reasoning": {"type": "string"},
        },
        "required": ["user_id", "text"],
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



client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
semaphore = asyncio.Semaphore(15)
            
async def eval_text_points(text: Dict[str, str], prompt: str, timeout: int = 30):
    """
    Evaluate text using OpenAI API with optimized retry logic and rate limiting.
    
    Args:
        text: Dictionary containing role and content for the message
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing the evaluation results
    """
    backoff = 0.1
    for attempt in range(3): 
        try:
            async with semaphore:
                resp = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[prompt, text],
                    response_format={
                        "type": "json_schema",
                        "json_schema": message_schema if prompt == message_prompt else conversation_schema
                    }
                )
                data = resp.choices[0].message.content
                return data
        except (RateLimitError, APIError, APITimeoutError) as e:
            print(f"API error on attempt {attempt + 1}: {type(e).__name__}")
            if attempt == 2:
                raise Exception(f"Failed to get response after 3 attempts. Last error: {str(e)}")
            await asyncio.sleep(backoff + random.random() * 0.1) 
            backoff = min(backoff * 1.5, 2.0)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}")

async def eval_multiple(texts: List[Dict[str, str]]):
    task = [eval_text_points(text, message_prompt) for text in texts]
    return await asyncio.gather(*task)

async def chunked_messages(conversation: List[Dict[str, str]]):
    
    chunks = []
    for i in range(0, len(conversation), 5):
        if i > 5:
            chunks.append(conversation[i-5:i])
        else:
            chunks.append(conversation[:i])
    return chunks

async def main():
    text1 = {"role": "user", "content": '''
            Context: [
            {
            user_id: 1234567899, text: I am racist.
            },
            {
            user_id: 1234567899, text: I like to eat meat.
            },
            ]
    
            message: {
            userid: 1234567892, text: Hey! That is not cool. Knock it off.
            }
            '''}
    
    text2 = {"role": "user", "content": '''
            [
            {
            user_id: 1234567899, text: I am racist.
            },
            {
            user_id: 1234567899, text: I like to eat meat.
            },
            {
             user_id: 1234567899, text: I like to eat fish.
            },
             {
             user_id: 1234567899, text: I like to eat fish, but I hate this. Why running feet?
             Yeah, why running feet? No running feet. This is dumb.
            },
             {
             user_id: 1234567899, text: I hate people. They are all stupid.
            },
             {
             user_id: 1234567890, text: Hey, let's try a more constructive approach to this problem, ok?
            },
             {
             user_id: 1234567890, text: Ok, not cool. I ask that you stop this. Please. It is not getting us anywhere,
             and I bet quite a few of us are being made uncomfortable. So please, think about the feelings of people around you.
             You are not working alone. We are all in this together. 
            },
             {
             user_id: 1234567891, text: Hey, not cool. Knock it off. 
            },
            {
             user_id: 1234567899, text: Oh confound you. I will not work in this group anymore. You are all f-ing idiots
            },
            ]
             '''
    }

    ''' Outline of what we have to do:

     Get the JSON data from the server.

     We must go in chunks of up to 5 messages at a time. The ending one.

     We go through, chunking them, formatting them correctly, and sending them to the third function
     I have defined. It is async. From there, we get the results and do our own fun logic.
     Very nice. 



     The AI calculates the things every 15 messages maybe. There should be a counter.
     It sends its data to the backend. But really just move this code over there. We can wrap it in an API if you really want.
     After 15, if it senses some bad vibes, if we deduce it has sensed some bad vibes from seeing its points, we tell everyone all about it.


     
     
     TODO: Add the kindness badges that are given to each other by the users. 

'''
    try:
        result = await eval_text_points(text2, conversation_prompt)
        print(result)

        result2 = await eval_text_points(text1, message_prompt)
        print(result2)

        # Then you call eval_multiple on the chunks and you deal with the results. 

       # if not -3 < result['points'] < 3:

         #  
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
# Make the input json object. Remember. Todo
