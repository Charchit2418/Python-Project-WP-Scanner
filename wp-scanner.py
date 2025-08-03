import requests
import json
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from colorama import init

# Initialize colorama (not used in GUI, optional)
init()

# Define the scan function
def scan_wordpress(target_url, output_box, status_label, progress):
    checks = ['xmlrpc.php', 'wp-cron.php', 'wp-config.php', 'wp-includes/', 'wp-content',
              'wp-json', 'robots.txt', 'sitemap.xml', '.htaccess', '.gitignore', '.git', '.log', 'readme.html']
    ua = {'user-agent': 'Mozilla/5.0'}

    # Normalize URL
    website = target_url.strip().replace("https://", "").replace("http://", "").rstrip("/")
    website = "https://" + website

    def log(msg, color="black"):
        output_box.insert(tk.END, msg + '\n', color)
        output_box.see(tk.END)

    output_box.delete('1.0', tk.END)
    status_label.config(text="Scanning in progress...", foreground="blue")
    progress.start()

    log("Scanning target: " + website, "blue")

    for i, path in enumerate(checks):
        url = f"{website}/{path}"
        try:
            response = requests.get(url, headers=ua, timeout=10)
            status_code = response.status_code
            source = response.text

            if "xmlrpc.php" in url:
                if "XML-RPC server accepts POST requests only" in source:
                    log(f"[+] XML-RPC is enabled :) URL: {url}", "green")
                else:
                    log("[!] XML-RPC is disabled :(", "red")

            elif "wp-config.php" in url:
                log_status("wp-config.php", source, url, log)

            elif "wp-cron.php" in url:
                log_status("wp-cron.php", source, url, log)

            elif "wp-includes" in url:
                if "Index of" in source:
                    log(f"[+] Directory listing enabled in /wp-includes/: {url}", "green")
                else:
                    log(f"[!] Directory listing disabled in /wp-includes/", "red")

            elif "wp-content" in url:
                if "Index of" in source:
                    log(f"[+] Directory listing enabled in /wp-content/: {url}", "green")
                else:
                    log(f"[!] Directory listing disabled in /wp-content/", "red")

            elif "wp-json" in url:
                if "rest_login_required" in source or "rest_cannot_access" in source:
                    log("[!] wp-json is disabled :(", "red")
                elif "description" in source or "endpoints" in source:
                    log(f"[+] wp-json is enabled :) URL: {url}", "green")
                    user_enum_url = f"{url}/wp/v2/users"
                    log("Trying to enumerate users...", "cyan")
                    log(f"User Enum URL: {user_enum_url}", "blue")
                    try:
                        user_data = requests.get(user_enum_url, headers=ua).json()
                        for user in user_data:
                            log(f"User found: {user['slug']}", "green")
                    except Exception:
                        log("[!] Failed to enumerate users", "red")

            elif "robots.txt" in url:
                if "User-agent" in source:
                    log(f"[+] robots.txt found: {url}", "green")
                    log(f"Content:\n{source}", "blue")
                else:
                    log("[!] robots.txt not found", "red")

            elif "sitemap.xml" in url:
                if status_code == 200:
                    log(f"[+] Sitemap found: {url}", "green")
                elif status_code == 302:
                    log(f"[+] Redirected to wp-sitemap.xml: {website}/wp-sitemap.xml", "green")
                else:
                    log("[!] Sitemap not found", "red")

            elif any(f in url for f in ['.htaccess', '.gitignore', '.git', '.log', 'readme.html']):
                if status_code == 200:
                    log(f"[+] {path} found: {url}", "green")
                elif status_code == 403:
                    log(f"[!] {path} found but forbidden to access", "red")
                else:
                    log(f"[!] {path} not found", "red")

        except Exception as e:
            log(f"[!] Error checking {url}: {str(e)}", "red")

    progress.stop()
    status_label.config(text="Scan complete ✅", foreground="green")


def log_status(file, source, url, log):
    if source.strip() == "":
        log(f"[!] {file} is not accessible :(", "red")
    else:
        log(f"[+] {file} is accessible! URL: {url}", "green")


# GUI Setup
def start_gui():
    root = tk.Tk()
    root.title("WordPress Recon Scanner")
    root.geometry("850x650")

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12))
    style.configure("TLabel", font=("Arial", 12))
    style.configure("TEntry", font=("Arial", 12))

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Enter WordPress Target URL:").pack(anchor="w")

    entry = ttk.Entry(frame, width=100)
    entry.pack(pady=10)

    # Output display box
    output_box = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=100, height=25, font=("Courier", 10))
    output_box.pack()

    # Define color tags
    for color in ["green", "red", "blue", "cyan"]:
        output_box.tag_config(color, foreground=color)

    # Status label
    status_label = ttk.Label(frame, text="Idle", foreground="grey")
    status_label.pack(pady=5)

    # Progress bar
    progress = ttk.Progressbar(frame, orient="horizontal", mode="indeterminate", length=200)
    progress.pack(pady=5)

    # Start scan function
    def start_scan():
        url = entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a target URL.")
            return
        threading.Thread(target=scan_wordpress, args=(url, output_box, status_label, progress), daemon=True).start()

    # Clear output
    def clear_output():
        output_box.delete('1.0', tk.END)
        status_label.config(text="Output cleared", foreground="gray")

    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=10)

    ttk.Button(button_frame, text="Start Scan", command=start_scan).pack(side="left", padx=10)
    ttk.Button(button_frame, text="Clear Output", command=clear_output).pack(side="left", padx=10)

    root.mainloop()


# Run the GUI
start_gui()
