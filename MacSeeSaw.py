#!/usr/bin/env python3

import subprocess
import re
import sys
import os
import random

# ANSI Color Codes
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[1;36m"
MAGENTA = "\033[1;35m"
BLUE = "\033[1;34m"
RESET = "\033[0m"

BANNER = f"""
{RED}
███╗   ███╗ █████╗  ██████╗    ███████╗███████╗███████╗    ███████╗ █████╗ ██╗    ██╗
████╗ ████║██╔══██╗██╔════╝    ██╔════╝██╔════╝██╔════╝    ██╔════╝██╔══██╗██║    ██║
██╔████╔██║███████║██║         ███████╗█████╗  █████╗      ███████╗███████║██║ █╗ ██║
██║╚██╔╝██║██╔══██║██║         ╚════██║██╔══╝  ██╔══╝      ╚════██║██╔══██║██║███╗██║
██║ ╚═╝ ██║██║  ██║╚██████╗    ███████║███████╗███████╗    ███████║██║  ██║╚███╔███╔╝
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚══════╝╚══════╝╚══════╝    ╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝ 
{RESET}
{BLUE}--Made with ❤ by r1k1xPriyam{RESET}
"""

def print_banner():
    print(BANNER)

def get_interfaces():
    try:
        output = subprocess.check_output(["ip", "link", "show"], text=True)
        interfaces = re.findall(r'\d+: (\w+):', output)
        return [iface for iface in interfaces if iface != 'lo']
    except Exception as e:
        print(f"{RED}Error getting interfaces: {e}{RESET}")
        sys.exit(1)

def get_current_mac(interface):
    try:
        output = subprocess.check_output(["ip", "link", "show", interface], text=True)
        match = re.search(r'link/ether ([0-9a-fA-F:]+)', output)
        return match.group(1) if match else None
    except Exception as e:
        print(f"{RED}Error getting MAC address: {e}{RESET}")
        return None

def validate_mac(mac):
    return bool(re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', mac))

def generate_random_mac():
    return "02:%02x:%02x:%02x:%02x:%02x" % tuple(random.randint(0, 255) for _ in range(5))

def change_mac(interface, new_mac):
    try:
        subprocess.run(["ip", "link", "set", "dev", interface, "down"], check=True)
        subprocess.run(["ip", "link", "set", "dev", interface, "address", new_mac], check=True)
        subprocess.run(["ip", "link", "set", "dev", interface, "up"], check=True)
        return True
    except Exception as e:
        print(f"{RED}Error changing MAC: {e}{RESET}")
        return False

def main():
    print_banner()
    
    if os.geteuid() != 0:
        print(f"{RED}This script must be run as root!{RESET}")
        sys.exit(1)

    interfaces = get_interfaces()
    if not interfaces:
        print(f"{RED}No network interfaces found!{RESET}")
        sys.exit(1)

    print(f"{CYAN}Available interfaces:{RESET}")
    for i, iface in enumerate(interfaces, 1):
        print(f"{YELLOW}[{i}] {iface}{RESET}")

    try:
        choice = int(input(f"\n{CYAN}Select interface [1-{len(interfaces)}]: {RESET}")) - 1
        interface = interfaces[choice]
    except (ValueError, IndexError):
        print(f"{RED}Invalid selection!{RESET}")
        sys.exit(1)

    current_mac = get_current_mac(interface)
    print(f"\n{YELLOW}Current MAC address: {GREEN}{current_mac}{RESET}")

    while True:
        new_mac = input(f"\n{CYAN}Enter new MAC address (XX:XX:XX:XX:XX:XX) or press ENTER for random: {RESET}").strip()
        if not new_mac:
            new_mac = generate_random_mac()
            print(f"{MAGENTA}Generated Random MAC: {new_mac}{RESET}")
            break
        elif validate_mac(new_mac):
            break
        print(f"{RED}Invalid MAC format!{RESET}")

    confirm = input(f"\n{MAGENTA}Confirm MAC change? [y/N]: {RESET}").lower()
    if confirm != 'y':
        print(f"{YELLOW}MAC change cancelled!{RESET}")
        sys.exit(0)

    if change_mac(interface, new_mac):
        updated_mac = get_current_mac(interface)
        print(f"\n{GREEN}Success! New MAC address: {updated_mac}{RESET}")
    else:
        print(f"\n{RED}Failed to change MAC address!{RESET}")

if __name__ == "__main__":
    main()
