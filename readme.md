## Product Overview
This tool exposes an API which can scan through a webpage and feed the content to an LLM to detect any compliance violation.
Compliance rules are currently being taken from a fixed URL defined in app.py 

## How to Run
1. Clone the project from Github
2. Create and activate virtual environment
3. Install requirements: pip install -r requirements.txt
4. Run app.py: python app.py
5. Test the API at  POST /check_compliance. Request data expects only a "url" parameter. This is the webpage that will be scanned for compliance violations.

