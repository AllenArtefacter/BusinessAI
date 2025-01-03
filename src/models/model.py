from src.chat.chat import Sender


def chat_to_gpt_conversation(chat):
    conversation = []
    for message in chat:
        if message.sender == Sender.USER:
            conversation.append({"role": "user", "content": message.prompt})
        elif message.sender == Sender.AI:
            conversation.append({"role": "assistant", "content": message.full_message})
        elif message.sender == Sender.SYSTEM:
            conversation.append({"role": "system", "content": message.full_message})
    return conversation
