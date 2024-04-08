import os
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


class LangchainChat:
    def __init__(self):
        # invoke google gemini api
        if "GOOGLE_API_KEY" not in os.environ:
            os.environ["GOOGLE_API_KEY"] = input("Provide your Google API key: ")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.0-pro-latest", convert_system_message_to_human=True
        )
        self.init_prompt_chain()

    def init_prompt_chain(self):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an assitant ChatBot. Answer all question to the best of you ability and keep your ansers brief. If you can't answer the question, reply 'I am sorry, i can't help you with that!'",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        self.chain = self.prompt | self.llm

        self.chat_history = ChatMessageHistory()

    def get_response(self, prompt):
        # add the prompt to chat_history.add_user_messages
        self.chat_history.add_user_message(prompt)
        # get the gemini response
        response = self.chain.invoke({"messages": self.chat_history.messages}).content
        # add the gemini response to history
        self.chat_history.add_ai_message(response)

        return response
