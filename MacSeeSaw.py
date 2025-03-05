#!/usr/bin/env python3

import subprocess
import re
import sys
import random
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

{BLUE}--Made with ❤ by r1k1xPriyam{RESET}
"""

VENDOR_MAC_PREFIXES = {
    "android": "00:1A:2B",
    "ios": "00:16:CB",
    "windows": "00:50:56",
    "linux": "00:0C:29"
}

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
        match = re.search(r'link/ether (\w\:\w\:\w\:\w\:\w\:\w)', output)
        return match.group(1) if match else None
    except Exception as e:
        print(f"{RED}Error getting MAC address: {e}{RESET}")
        return None

def validate_mac(mac):
    """Validate MAC address format"""
    return re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', mac)

def generate_random_mac(prefix):
    """Generate a random MAC address with the given prefix"""
    return f"{prefix}:{random.randint(0x00, 0xFF):02X}:{random.randint(0x00, 0xFF):02X}:{random.randint(0x00, 0xFF):02X}"

def change_mac(interface, new_mac):
    """Change MAC address of specified interface"""
    try:
        subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "down"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "address", new_mac], check=True)
        subprocess.run(["sudo", "ip", "link", "set", "dev", interface, "up"], check=True)
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

    print("\nChoose MAC address option:")
    print(f"{CYAN}1. Enter custom MAC address")
    print(f"2. Use a vendor-based random MAC (Android, iOS, Windows, Linux)")
    print(f"3. Randomly set MAC address or use default (press ENTER){RESET}")

    option = input(f"\n{CYAN}Select option [1-3]: {RESET}")
    
    if option == "1":
        new_mac = input(f"\n{CYAN}Enter new MAC address: {RESET}")
    elif option == "2":
        vendor = input(f"\n{CYAN}Enter vendor name: {RESET}").lower()
        new_mac = generate_random_mac(VENDOR_MAC_PREFIXES.get(vendor, "00:16:3E"))
    else:
        new_mac = generate_random_mac("00:16:3E")
    
    if change_mac(interface, new_mac):
        print(f"\n{GREEN}Success! New MAC address: {new_mac}{RESET}")
    else:
        print(f"\n{RED}Failed to change MAC address!{RESET}")

if __name__ == "__main__":
    main()
