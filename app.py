import asyncio
import json
import gspread
from openai import AsyncOpenAI
from pygrok import Grok


open_ai_key = ""


client = AsyncOpenAI(
    api_key=open_ai_key
)

gc = gspread.service_account()
sh = gc.open("grokker-dataset")


def generate_prompt(log_line: str) -> str:
    return f"""You are a grok pattern suggesting bot who takes in input as log_line and gives out grok patterns for the log line. You are given a log line: {log_line}. You have to suggest grok patterns for the log line. The output of json has an array of objects. Each object has a pattern and a confidence score.
    The format of output should be this. Even if there is only one output the format should be in array of objects.
    [
`       {{
            "pattern" : "pattern1",
            "confidence": "range from 0 to 1"
        }},
        {{
            "pattern" : "pattern2",
            "confidence": "range from 0 to 1"
        }}
    ]
    """


async def get_gpt_response(log_line: str) -> str:
    chat_completion = await client.chat.completions.create(
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
                "content": "You are a helpful assistant designed to output JSON."},
            {
                "role": "user",
                "content": generate_prompt(log_line="[2024-03-09T12:24:13.794Z] WARN  [mediasoup:Channel]: [pid:42] RTC::Transport::ReceiveRtpPacket() | no suitable Producer for received RTP packet [ssrc:419734590, payloadType:111]"),
            },
            {
                "role": "system",
                "content": """
  [
    {"pattern": "\\[%{TIMESTAMP_ISO8601:timestamp}\\] %{LOGLEVEL:loglevel}  \\[%{DATA:source}\\]: \\[pid:%{NUMBER:pid}\\] %{DATA:message} \\[ssrc:%{NUMBER:ssrc}, payloadType:%{NUMBER:payloadType}\\]", "confidence": 0.85},
    {"pattern": "\\[%{TIMESTAMP_ISO8601:logdate}\\] %{WORD:loglevel}  \\[%{NOTSPACE:info}\\]: \\[pid:%{NUMBER:process_id}\\] %{GREEDYDATA:log_message} \\[ssrc:%{NUMBER:ssrc}, payloadType:%{NUMBER:payloadType}\\]", "confidence": 0.75}
  ]
  """,
            },
            {
                "role": "user",
                "content": generate_prompt(log_line=log_line),
            }
        ],
        model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content


async def check_grok_pattern(log_line: str) -> str:
    grok_response = await get_gpt_response(log_line)
    try:
        grok_response = json.loads(grok_response)
        # Here is the json response:
        # {'pattern': [{'pattern': '\\[%{DAY:day} %{MONTH:month} %{MONTHDAY:monthday} %{TIME:time} %{YEAR:year}\\] \\[%{WORD:loglevel}\\] \\[client %{IP:client_ip}\\] %{GREEDYDATA:message}', 'confidence': 0.9}]}
        # parse it

        try:
            grok_patterns = grok_response["pattern"]
            print(grok_patterns)
            for pattern in grok_patterns:
                grok_pattern = pattern["pattern"]
                with open("android.csv", "a") as f:
                    output = f"{log_line.strip()},{grok_pattern}\n"
                    f.write(output)
        except:
            print("Error while parsing grok pattern")
            return "Error while parsing grok pattern"
    except json.JSONDecodeError:
        print(f"Error while parsing json {grok_response}")
        return "Error while parsing json"


async def process_log_file():
    with open('Android.log', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f):
            try:
                if i % 1000 == 0:
                    print(f"Processed {i} lines")
                    await check_grok_pattern(line)
            except:
                print(f"Error while processing line {line}")
                pass

if __name__ == "__main__":
    asyncio.run(process_log_file())
