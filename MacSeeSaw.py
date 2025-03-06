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
BLUE = "\033[1;34m"
RESET = "\033[0m"

BANNER = f"""
{RED}
███╗   ███╗ █████╗  ██████╗    ███████╗███████╗███████╗
████╗ ████║██╔══██╗██╔════╝    ██╔════╝██╔════╝██╔════╝
██╔████╔██║███████║██║         ███████╗█████╗  █████╗  
██║╚██╔╝██║██╔══██║██║         ╚════██║██╔══╝  ██╔══╝  
██║ ╚═╝ ██║██║  ██║╚██████╗    ███████║███████╗███████╗
╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚══════╝╚══════╝╚══════╝
{RESET}
{BLUE}-- Made with ❤ by r1k1xPriyam{RESET}
"""

# Vendor MAC Prefixes
VENDOR_MAC_PREFIXES = {
    "Android": ["02:1A:11", "06:5B:D2", "0A:9C:F3"],
    "iOS": ["02:5A:13", "06:3B:A1", "0A:7D:E4"],
    "Windows": ["00:1A:2B", "00:26:9E", "00:50:56"],
    "Linux": ["00:16:3E", "52:54:00", "02:42:AC"]
}

def print_banner():
    print(BANNER)

def get_interfaces():
    """Get network interfaces"""
    output = subprocess.check_output(["ip", "link", "show"]).decode()
    return [iface for iface in re.findall(r'\d+: (\w+):', output) if iface != 'lo']

def get_current_mac(interface):
    """Retrieve current MAC address"""
    output = subprocess.check_output(["ip", "link", "show", interface]).decode()
    match = re.search(r'link/ether (\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)', output)
    return match.group(1) if match else None

def validate_mac(mac):
    """Validate MAC address"""
    return re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', mac)

def generate_random_mac():
    """Generate random MAC address"""
    return f"02:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}"

def generate_vendor_mac(vendor):
    """Generate MAC based on vendor"""
    if vendor in VENDOR_MAC_PREFIXES:
        return f"{random.choice(VENDOR_MAC_PREFIXES[vendor])}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}"
    return None

def change_mac(interface, new_mac):
    """Change MAC address"""
    try:
        subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "down"], check=True)
        time.sleep(1)
        subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "address", new_mac], check=True)
        time.sleep(1)
        subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "up"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def auto_mac_changer(interface, generate_mac_func, interval):
    """Automatically change MAC at intervals"""
    try:
        print(f"{CYAN}Auto MAC change enabled. Press Ctrl+C to stop.{RESET}")
        while True:
            new_mac = generate_mac_func()
            print(f"\n{GREEN}Changing MAC to: {new_mac}{RESET}")
            if change_mac(interface, new_mac):
                print(f"{GREEN}MAC changed successfully!{RESET}")
            else:
                print(f"{RED}MAC change failed!{RESET}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Auto MAC Changer stopped.{RESET}")

def main():
    print_banner()
    
    if os.geteuid() != 0:
        print(f"{RED}Run this script as root!{RESET}")
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
    print(f"\n{YELLOW}Current MAC: {GREEN}{current_mac}{RESET}")

    print(f"\n{CYAN}Choose MAC address option:{RESET}")
    print(f"[1] Enter custom MAC")
    print(f"[2] Generate random MAC")
    print(f"[3] Choose vendor MAC (Android/iOS/Windows/Linux)")
    print(f"[4] Default (Press ENTER to skip)")

    mac_choice = input(f"\n{CYAN}Enter choice: {RESET}")

    if mac_choice == '1':
        while True:
            new_mac = input(f"\n{CYAN}Enter new MAC (XX:XX:XX:XX:XX:XX): {RESET}")
            if validate_mac(new_mac):
                break
            print(f"{RED}Invalid MAC format!{RESET}")
    elif mac_choice == '2':
        new_mac = generate_random_mac()
    elif mac_choice == '3':
        vendor = input(f"\n{CYAN}Enter vendor (Android/iOS/Windows/Linux): {RESET}").capitalize()
        new_mac = generate_vendor_mac(vendor) or generate_random_mac()
    else:
        print(f"{YELLOW}Keeping current MAC!{RESET}")
        sys.exit(0)

    interval = input(f"\n{CYAN}Set interval in seconds (Press ENTER to skip): {RESET}")
    if interval.isdigit():
        interval = int(interval)
        auto_mac_changer(interface, lambda: generate_vendor_mac(vendor) if mac_choice == '3' else generate_random_mac(), interval)
    else:
        if change_mac(interface, new_mac):
            print(f"\n{GREEN}Success! New MAC: {new_mac}{RESET}")

if __name__ == "__main__":
    main()
