import sys

def main():
    print("Welcome to CarGPT! How can I assist you today?")

    while True:
        user_input = input("> ")

        if user_input.lower() == 'exit':
            print("Goodbye!")
            sys.exit()

        # Process user_input here later
        print(f"You said: {user_input}") # Placeholder

if __name__ == "__main__":
    main() 