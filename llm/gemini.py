import os
import asyncio
import google.generativeai as genai


class Gemini:
    def __init__(self):
        api_key = "AIzaSyCHIt0htsxDFw5vVmgb39BUE58K-mBWD0g"  # os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.0-pro-latest")

    def get_response(self, text):
        response = self.model.generate_content(text, stream=True)
        text_response = r""
        for chunk in response:
            text_response += chunk.text

        return text_response


# if __name__ == "__main__":
#     gemini = Gemini()
#     response = gemini.get_response("Tell about the property of water?")
#     print(response)
