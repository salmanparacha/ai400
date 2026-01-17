"""
Custom Tools Example

Demonstrates creating custom tools with the @tool decorator.
"""

from strands import Agent, tool
from strands_tools import calculator, current_time

# Define custom tools
@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count occurrences of a specific letter in a word.

    Args:
        word: The input word to search in
        letter: The specific letter to count

    Returns:
        The number of occurrences of the letter in the word
    """
    if not isinstance(word, str) or not isinstance(letter, str):
        return 0
    if len(letter) != 1:
        raise ValueError("The 'letter' parameter must be a single character")
    return word.lower().count(letter.lower())

@tool
def word_reverser(text: str) -> str:
    """
    Reverse the characters in a text string.

    Args:
        text: The text to reverse

    Returns:
        The reversed text
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")
    return text[::-1]

@tool
def text_analyzer(text: str) -> dict:
    """
    Analyze text and return statistics.

    Args:
        text: The text to analyze

    Returns:
        Dictionary with word count, character count, and sentence count
    """
    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    words = text.split()
    sentences = text.count('.') + text.count('!') + text.count('?')

    return {
        "word_count": len(words),
        "character_count": len(text),
        "sentence_count": max(sentences, 1),
        "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
    }

def main():
    # Create agent with both built-in and custom tools
    agent = Agent(
        tools=[calculator, current_time, letter_counter, word_reverser, text_analyzer],
        system_prompt="You are a helpful assistant with text analysis and calculation capabilities."
    )

    print("=" * 50)
    print("Custom Tools Example")
    print("=" * 50)

    # Example queries
    queries = [
        "What is the time right now?",
        "Calculate 42 * 17",
        "How many letter R's are in the word 'strawberry'?",
        "Reverse the word 'hello'",
        "Analyze this text: 'Hello world. How are you? I am fine.'"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{i}. {query}")
        response = agent(query)
        print(f"Response: {response.message}\n")

    # Interactive mode
    print("\nInteractive mode - ask your own question (or press Enter to exit):")
    while True:
        user_query = input("Your question: ")
        if not user_query.strip():
            break
        response = agent(user_query)
        print(f"Response: {response.message}\n")

if __name__ == "__main__":
    main()
