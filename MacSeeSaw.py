#!/usr/bin/env python3

import subprocess
import re
import sys
import random
import time
import os

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

{BLUE}-- Made with ❤ by r1k1xPriyam{RESET}
"""

def print_banner():
    print(BANNER)

def get_interfaces():
    """Get list of network interfaces"""
    try:
        output = subprocess.check_output(["ip", "link", "show"]).decode()
        interfaces = re.findall(r'\d+: (\w+):', output)
        return [iface for iface in interfaces if iface != 'lo']
    except Exception as e:
        print(f"{RED}Error getting interfaces: {e}{RESET}")
        sys.exit(1)

def get_current_mac(interface):
    """Get current MAC address of specified interface"""
    try:
        output = subprocess.check_output(["ip", "link", "show", interface]).decode()
        match = re.search(r'link/ether (\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)', output)
        return match.group(1) if match else None
    except Exception as e:
        print(f"{RED}Error getting MAC address: {e}{RESET}")
        return None

def validate_mac(mac):
    """Validate MAC address format"""
    return re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', mac)

def generate_random_mac():
    """Generate a valid random MAC address"""
    first_byte = random.choice(['02', '06', '0A', '0E'])  # Locally administered MAC
    return f"{first_byte}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}"

def change_mac(interface, new_mac):
    """Change MAC address of specified interface"""
    try:
        subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "down"], check=True)
        time.sleep(1)
        subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "address", new_mac], check=True)
        time.sleep(1)
        subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "up"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}Error changing MAC: {e}{RESET}")
        return False

def auto_mac_changer(interface, interval):
    """Automatically change MAC address at user-defined intervals"""
    try:
        print(f"{CYAN}Starting Auto MAC Changer. Press Ctrl+C to stop.{RESET}")
        while True:
            new_mac = generate_random_mac()
            print(f"\n{MAGENTA}Changing MAC to: {GREEN}{new_mac}{RESET}")
            if change_mac(interface, new_mac):
                print(f"{GREEN}MAC changed successfully!{RESET}")
            else:
                print(f"{RED}MAC change failed!{RESET}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Auto MAC Changer stopped.{RESET}")

def main():
    print_banner()
    
    # Check root privileges
    if os.geteuid() != 0:
        print(f"{RED}This script must be run as root!{RESET}")
        sys.exit(1)
    
    # Get available interfaces
    interfaces = get_interfaces()
    if not interfaces:
        print(f"{RED}No network interfaces found!{RESET}")
        sys.exit(1)

    # Interface selection
    print(f"{CYAN}Available interfaces:{RESET}")
    for i, iface in enumerate(interfaces, 1):
        print(f"{YELLOW}[{i}] {iface}{RESET}")
    
    try:
        choice = int(input(f"\n{CYAN}Select interface [1-{len(interfaces)}]: {RESET}")) - 1
        interface = interfaces[choice]
    except (ValueError, IndexError):
        print(f"{RED}Invalid selection!{RESET}")
        sys.exit(1)

    # Get current MAC
    current_mac = get_current_mac(interface)
    print(f"\n{YELLOW}Current MAC address: {GREEN}{current_mac}{RESET}")

    print(f"\n{CYAN}Choose MAC address option:{RESET}")
    print(f"[1] Enter custom MAC")
    print(f"[2] Generate random MAC")
    print(f"[3] Default (Press ENTER to skip)")

    mac_choice = input(f"\n{CYAN}Enter choice: {RESET}")
    if mac_choice == '1':
        while True:
            new_mac = input(f"\n{CYAN}Enter new MAC address (XX:XX:XX:XX:XX:XX): {RESET}")
            if validate_mac(new_mac):
                break
            print(f"{RED}Invalid MAC format!{RESET}")
    elif mac_choice == '2':
        new_mac = generate_random_mac()
        print(f"\n{MAGENTA}Generated Random MAC: {GREEN}{new_mac}{RESET}")
    else:
        print(f"{YELLOW}Keeping current MAC!{RESET}")
        sys.exit(0)

    interval_choice = input(f"\n{CYAN}Enable auto MAC change? (y/N): {RESET}").lower()
    if interval_choice == 'y':
        interval = int(input(f"\n{CYAN}Enter time interval in seconds: {RESET}"))
        auto_mac_changer(interface, interval)
    else:
        # Perform MAC change once
        if change_mac(interface, new_mac):
            print(f"\n{GREEN}Success! New MAC address: {new_mac}{RESET}")
        else:
            print(f"\n{RED}MAC address change failed!{RESET}")

if __name__ == "__main__":
    main()
