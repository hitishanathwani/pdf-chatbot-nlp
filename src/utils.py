from datetime import datetime

def export_chat_history(chat_history):
    export_text = f"Chat History Export\n"
    export_text += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    export_text += "=" * 50 + "\n\n"

    for message in chat_history:
        if message["role"] == "user":
            export_text += f"You: {message['content']}\n\n"
        else:
            export_text += f"Assistant: {message['content']}\n"
            if message.get("confidence"):
                export_text += f"Confidence: {message['confidence']:.0%}\n"
            if message.get("sources"):
                export_text += "Sources:\n"
                for src in message["sources"]:
                    export_text += f"  - {src['file']} (Page {src['page']})\n"
            export_text += "\n"

    return export_text