# OpenAI Screenshot Tool

This tool uses OpenAI's new function calling feature to process natural language commands and take screenshots of webpages.

## Setup

1. Clone this repository.
2. Install the required Python packages: `pip install -r requirements.txt`
3. Set up a `.env` file in the root directory of the project, and add your OpenAI API key:

    ```
    OPENAI_API_KEY=your-api-key-here
    ```

## Usage

Run the script with a command to take a screenshot of a webpage. For example:

```bash
python main.py "Take a screenshot of https://figma.com"
```
The screenshot will be saved as screenshot.png in the project directory.

Please replace `your-api-key-here` with your actual OpenAI API key in the `.env-example` and rename the file to .env.
