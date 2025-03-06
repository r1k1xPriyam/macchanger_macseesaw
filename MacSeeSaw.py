#!/usr/bin/env python3

import subprocess
import re
import sys
import os
import time
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

VENDORS = {
    "Android": "00:1A:2B",
    "iOS": "00:16:CB",
    "Windows": "00:50:56",
    "Linux": "00:0C:29"
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
        match = re.search(r'link/ether ([0-9a-fA-F:]+)', output)
        return match.group(1) if match else None
    except Exception as e:
        print(f"{RED}Error getting MAC address: {e}{RESET}")
        return None

def validate_mac(mac):
    """Validate MAC address format"""
    return re.match(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$', mac)

def generate_random_mac(vendor_prefix=None):
    """Generate a random MAC address"""
    mac = vendor_prefix if vendor_prefix else ":".join(f"{random.randint(0, 255):02x}" for _ in range(3))
    mac += ":" + ":".join(f"{random.randint(0, 255):02x}" for _ in range(3))
    return mac.lower()

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

def auto_change_mac(interface, interval):
    """Automatically change MAC address at a user-defined interval"""
    try:
        while True:
            new_mac = generate_random_mac()
            print(f"{YELLOW}\nChanging MAC to: {GREEN}{new_mac}{RESET}")
            change_mac(interface, new_mac)
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"{RED}\nAuto MAC change stopped!{RESET}")

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
    
    mode = input(f"\n{CYAN}Enable Auto MAC Change Mode? (y/N): {RESET}").strip().lower()
    if mode == "y":
        interval = int(input(f"{CYAN}Enter time interval (seconds): {RESET}"))
        auto_change_mac(interface, interval)
        sys.exit(0)
    
    print(f"{CYAN}\nChoose MAC Address Option:{RESET}")
    print(f"{YELLOW}1. Enter Custom MAC{RESET}")
    print(f"{YELLOW}2. Choose Vendor MAC{RESET}")
    print(f"{YELLOW}3. Random MAC (Press ENTER for default){RESET}")
    
    option = input(f"\n{CYAN}Select option [1-3]: {RESET}").strip()
    
    if option == "1":
        new_mac = input(f"{CYAN}Enter new MAC address: {RESET}")
    elif option == "2":
        vendor = input(f"{CYAN}Choose Vendor (Android/iOS/Windows/Linux): {RESET}")
        new_mac = generate_random_mac(VENDORS.get(vendor))
    else:
        new_mac = generate_random_mac()
    
    change_mac(interface, new_mac)
    print(f"\n{GREEN}Success! New MAC: {new_mac}{RESET}")

if __name__ == "__main__":
    main()
