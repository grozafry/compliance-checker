import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import openai
import re

app = Flask(__name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")

COMPLIANCE_POLICY_URL = "https://stripe.com/docs/treasury/marketing-treasury"
MAX_TOKENS = 1000

def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    return soup.get_text().strip()

def call_openai_api(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "You are an expert compliance auditor with a knack for looking through the details."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=MAX_TOKENS,
        temperature=0.1,
    )

    message_content = response['choices'][0]['message']['content']
    cleaned_content = message_content.strip()
    cleaned_content = re.sub(r'```json|```', '', cleaned_content).strip()

    return cleaned_content

def check_compliance(webpage_text, compliance_policy_text):
    
    prompt = f"""
    Given the following compliance policy:
    {compliance_policy_text}

    And the following webpage content:
    {webpage_text}

    Identify any violations of the compliance policy in the webpage content. 
    Return the findings as a list of dictionaries, where each dictionary contains:
    1. 'rule': The specific rule that was violated
    2. 'violation': The text from the webpage that violates the rule
    
    If no violations are found, return an empty list.
    In all cases, ONLY a list should be returned.
    """

    try:
        response_content = call_openai_api(prompt)
        violations = eval(response_content)
        return violations
    except Exception as e:
        print(f"Error in check_compliance: {str(e)}")
        raise e

@app.route('/check_compliance', methods=['POST'])
def api_check_compliance():
    """
    POST Request
    {
        "url": "https://mercury.com/"
    }

    Response 
    {
    "violations": [
            {
                "rule": "Terms to Avoid - Avoid using 'banking' when not a licensed bank",
                "violation": "Powerful banking. Simplified finances."
            },
            {
                "rule": "Terms to Avoid - Avoid using 'bank account' when not a licensed bank",
                "violation": "Your bank account should do more than hold your money."
            }
        ]
    }
        
    """
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        webpage_text = extract_text_from_url(url)
        compliance_policy_text = extract_text_from_url(COMPLIANCE_POLICY_URL)
        violations = check_compliance(webpage_text, compliance_policy_text)
        return jsonify({"violations": violations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port="5000")