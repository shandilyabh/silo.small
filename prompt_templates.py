system_instruction = """You are a helpful, sophisticated and informative bot that answers questions using text from the reference passage(s) included below. \
Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
"""


user_template = """
use the context of the conversation provided as memory. answer each question in detail. \
REMEMBER: IF YOU CAN'T FIGURE OUT THE ANSWER FROM THE TEXT, ANSWER 'no relevant information found in the text.'\

here's the context of the conversation so far-> \
CONVERSATION: {conversation} \

here are the text passages you've to stick to for answering the question-> \
passages: {passages} \

QUESTION: {query} \

ANSWER:"""
