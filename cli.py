import argparse
from agent.agent import Agent
from computers.config import *
from computers.default import *
from computers import computers_config
import os


def acknowledge_safety_check_callback(message: str) -> bool:
    response = input(
        f"Safety Check Warning: {message}\nDo you want to acknowledge and proceed? (y/n): "
    ).lower()
    return response.lower().strip() == "y"


def main():
    parser = argparse.ArgumentParser(
        description="Select a computer environment from the available options."
    )
    parser.add_argument(
        "--computer",
        choices=computers_config.keys(),
        help="Choose the computer environment to use.",
        default="local-playwright",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Initial input to use instead of asking the user.",
        default=None,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for detailed output.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show images during the execution.",
    )
    parser.add_argument(
        "--start-url",
        type=str,
        help="Start the browsing session with a specific URL (only for browser environments).",
        default="https://bing.com",
    )
    parser.add_argument(
        "--token-usage-file",
        type=str,
        help="File to save/load token usage history.",
        default="token_usage.json",
    )
    args = parser.parse_args()
    ComputerClass = computers_config[args.computer]

    with ComputerClass() as computer:
        agent = Agent(
            computer=computer,
            acknowledge_safety_check_callback=acknowledge_safety_check_callback,
        )
        
        # Load previous token usage if file exists
        if os.path.exists(args.token_usage_file):
            agent.load_token_usage(args.token_usage_file)
            
        items = []

        if args.computer in ["browserbase", "local-playwright"]:
            if not args.start_url.startswith("http"):
                args.start_url = "https://" + args.start_url
            agent.computer.goto(args.start_url)

        try:
            while True:
                try:
                    user_input = args.input or input("> ")
                    if user_input == "exit":
                        break
                except EOFError as e:
                    print(f"An error occurred: {e}")
                    break
                items.append({"role": "user", "content": user_input})
                output_items = agent.run_full_turn(
                    items,
                    print_steps=True,
                    show_images=args.show,
                    debug=args.debug,
                )
                items += output_items
                args.input = None
        finally:
            # Save token usage before exiting
            agent.save_token_usage(args.token_usage_file)
            usage = agent.token_tracker.get_current_usage()
            print("\nFinal Token Usage Summary:")
            print(f"Total prompt tokens: {usage['prompt_tokens']}")
            print(f"Total completion tokens: {usage['completion_tokens']}")
            print(f"Total tokens: {usage['total_tokens']}")
            print(f"Total estimated cost: ${usage['cost']:.4f}")


if __name__ == "__main__":
    main()
