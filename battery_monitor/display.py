from colorama import init, Fore, Style

# Initialize color support
init(autoreset=True)


def show_basic_status(status):
    print("=== Basic Battery Status ===")
    print(f"{Fore.GREEN}Charge: {status['percent']}%{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Plugged In: {'Yes' if status['plugged'] else 'No'}{Style.RESET_ALL}")

    if status['secsleft'] != -1:
        minutes = status['secsleft'] // 60
        print(f"{Fore.YELLOW}Estimated Runtime: {minutes} minutes{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Estimated Runtime: Unavailable{Style.RESET_ALL}")
    print()


def show_advanced_info(info):
    print("=== Advanced Battery Information ===")
    for key, value in info.items():
        label = key.replace('_', ' ').title()
        print(f"{Fore.MAGENTA}{label}: {value}{Style.RESET_ALL}")
    print()