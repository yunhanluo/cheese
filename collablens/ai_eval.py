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
            "user_id": {"type": "string"},
            "points": {"type": "integer"},
            "reasoning": {"type": "string"},
        },
        "required": ["user_id", "text", "reasoning"],
        "additionalProperties": False
    },
}

response_schema = {
    "name": "ai_response",
    "schema": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "text": {"type": "string"},
            "priority": {"type": "string"},
        },
        "required": ["user_id", "text", "priority"],
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

async def eval_multiple(texts, prompt):
    task = [eval_text_points(text, prompt) for text in texts]
    return await asyncio.gather(*task)

async def chunked_messages(conversation):
    chunks = []
    for i in range(0, len(conversation), 5):
        if i > 5:
            chunks.append(conversation[i-5:i])
        else:
            chunks.append(conversation[:i])
    return chunks

async def main():
    text = [
    {'sender': 1234567899, 'data': 'I am racist.'},
    {'sender': 1234567899, 'data': 'I like to eat meat.'},
    {'sender': 1234567892, 'data': 'Hey! That is not cool. Knock it off.'} # Sample Data. Data should follow this format.
]
 # Here's some data I wrote. But it is not formatted correctly, so womp womp.

    text1 = {"role": "user", "content": '''
            
             {sender: 1234567899, data: 'I am racist.'
            },
            {
            data: 1234567899, data: I like to eat meat.
            },
            userid: 1234567892, data: Hey! That is not cool. Knock it off.
            }
            '''}
    
    text2 = {"role": "user", "content": '''
            [
            {
            sender: 1234567899, 
            data: I am racist.
            },
            {
            sender: 1234567899, data: I like to eat meat.
            },
            {
             sender: 1234567899, data: I like to eat fish.
            },
             {
             sender: 1234567899, data: I like to eat fish, but I hate this. Why running feet?
             Yeah, why running feet? No running feet. This is dumb.
            },
             {
             sender: 1234567899, data: I hate people. They are all stupid.
            },
             {
             sender: 1234567890, data: Hey, let's try a more constructive approach to this problem, ok?
            },
             {
             sender: 1234567890, data: Ok, not cool. I ask that you stop this. Please. It is not getting us anywhere,
             and I bet quite a few of us are being made uncomfortable. So please, think about the feelings of people around you.
             You are not working alone. We are all in this together. 
            },
             {
             sender: 1234567891, data: Hey, not cool. Knock it off. 
            },
            {
             sender: 1234567899, data: Oh confound you. I will not work in this group anymore. You are all f-ing idiots
            },
            ]
             '''
    }

    ''' Outline of what we have to do:

     Get the JSON data from the server. Drop those fields, to get something like the one that's on the Google Doc. Clean it, and then send it over.
     Remember, calls must make the prompts be the string versions, like "conversation_prompt" "response_prompt" etc.

     The AI calculates the things every 15 messages maybe. There should be a counter.
     It sends its data to the backend. But really just move this code over there. We can wrap it in an API if you really want.
     After 15, if it senses some bad vibes, if we deduce it has sensed some bad vibes from seeing its points, we tell everyone all about it.


     
     
     TODO: Add the kindness badges that are given to each other by the users. 

'''
    try:
        result = await eval_text_points(text, "message_prompt")
        print(result)

     #   result2 = await eval_text_points(text1, "message_prompt")
     #   print(result2)

     #   result3 = await eval_multiple(text2, "conversation_prompt")

      #  result3.filter(lambda x: not -3 < x < 3)
     #   print(result3)

      # Then you call eval_multiple on the chunks and you deal with the results. 

       # if not -3 < result['points'] < 3:

         #  
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
