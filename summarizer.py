import json
import re
import config
from google import genai

client = genai.Client(api_key=config.GEMINI_API_KEY)


def extract_json(text):
    """
    Extract the first JSON object from a string.
    """
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found")

    json_str = match.group(0)

    return json.loads(json_str)


def format_spam(data):

    message = f"*Potential Spam Email*\n\n"
    message += f"*Subject:* {data.get('subject','Unknown')}\n"

    if data.get("reasoning"):
        message += "\n*Reason*"
        for r in data["reasoning"]:
            message += f"\n- {r}"

    if data.get("keywords"):
        message += "\n\n*Keywords detected*"
        for k in data["keywords"]:
            message += f"\n- {k}"

    return message


def format_not_spam(data):
    """
    Convert parsed JSON into a WhatsApp friendly message
    """

    if data["status"] == "spam":

        message = f"""*Spam Detected*

*Subject:* {data.get("subject", "Unknown")}

*Reasoning:*"""

        for r in data.get("reasoning", []):
            message += f"\n- {r}"

        if data.get("keywords"):
            message += "\n\n*Keywords:*"
            for k in data["keywords"]:
                message += f"\n- {k}"

        return message

    # Normal email
    message = f"*Subject:* {data['subject']}\n"

    if data.get("importance") == "important":
        message += "*Importance:* HIGH\n"

    if data.get("summary"):
        message += "\n*Summary*"
        for s in data["summary"]:
            message += f"\n- {s}"

    if data.get("links"):
        message += "\n\n*Links Worth Opening*"
        for link in data["links"]:
            url = link.get("url")
            desc = link.get("description", "")
            message += f"\n- {desc}\n  {url}"

    if data.get("actions"):
        message += "\n\n*Actions*"
        for a in data["actions"]:
            message += f"\n- {a}"

    return message


def summarize_email(text):

    prompt = """
You are an intelligent email triage assistant.

Your job is to analyze emails and return a short structured report suitable for sending summaries to WhatsApp.

IMPORTANT OUTPUT RULES:
- Output MUST be valid JSON.
- Do NOT include markdown, explanations, or code fences.
- Do NOT include emojis.
- Only return the JSON object.
- Follow the schema exactly.

--------------------------------

First determine the email type:
1. spam / phishing / scam
2. important / urgent
3. normal informational email

--------------------------------

If the email appears to be SPAM or PHISHING:

Return JSON in this format:

{
  "status": "spam",
  "subject": "<email subject>",
  "reasoning": [
    "<short reason why it looks like spam>",
    "<another signal if applicable>"
  ],
  "keywords": [
    "<suspicious word or phrase>",
    "<another suspicious phrase>"
  ]
}

Rules:
- reasoning should explain the indicators used to classify it as spam.
- keywords should contain suspicious phrases or patterns found in the email.

Do NOT include summaries, links, or actions.

--------------------------------

If the email is NOT spam:

Return JSON in this format:

{
  "status": "not_spam",
  "importance": "important | normal",
  "subject": "<email subject>",
  "summary": [
    "<key point>",
    "<key point>"
  ],
  "links": [
    {
      "url": "<link>",
      "description": "<why this link may be useful>"
    }
  ],
  "actions": [
    "<task, deadline, or required response>"
  ]
}

Field rules:
- summary: list of key information points.
- links: only include useful or relevant links.
- actions: tasks, deadlines, meetings, or responses required.
- If no links or actions exist, return an empty list.

--------------------------------

General guidelines:

- Maximum 5 summary points.
- Be concise.
- Extract meaningful information only.
- If the email appears financially, legally, or operationally important, set importance to "important".
- Do not invent information if unclear.
- For very long link, just indicate the intent of the link instead of the whole link

--------------------------------

Email:""" + f"""{text}"""

    response = client.models.generate_content(
        model=config.MODEL,
        contents=prompt
    )
    data = extract_json(response.text)

    if data['status'] == 'not_spam':
        message = format_not_spam(data)
    else:
        message = format_spam(data)

    return message
