import paramiko
import time
import os
import subprocess
from datetime import datetime

LOG_DIR = r"C:\it"
os.makedirs(LOG_DIR, exist_ok=True)

AP_LIST = [
    {"host": "0.0.0.0", "username": "utente", "password": "******"},
    {"host": "0.0.0.0", "username": "utente", "password": "******"},
]

def log_message(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(os.path.join(LOG_DIR, "ap_reboot.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")

def ping_test(host, count=3):
    """Test ping per verificare disponibilità AP"""
    try:
        result = subprocess.run(['ping', '-n', str(count), host], 
                              capture_output=True, text=True, timeout=15)
        return result.returncode == 0
    except:
        return False

def reboot_ap(ap):
    host = ap["host"]
    log_message(f"Connecting to {host}")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, username=ap["username"], password=ap["password"], timeout=10)
        log_message(f"Connected to {host}")
        
        shell = ssh.invoke_shell()
        time.sleep(2)  # Prompt stabile
        
        # Pulisci buffer iniziale
        shell.recv(4096)
        
        # Invia reboot
        shell.send("reboot\n")
        time.sleep(3)  # Attesa risposta completa
        
        # LEGGE output per conferma
        output = shell.recv(4096).decode('utf-8', errors='ignore')
        log_message(f"OUTPUT da {host}: {output.strip()}")
        
        if "EnterpriseWLAN is going to reboot" in output:
            log_message(f"CONFIRMATO: {host} sta riavviando!")
        else:
            log_message(f"AVVISO: Nessuna conferma reboot da {host}")
        
        ssh.close()
        
        # Test ping pre-reboot
        log_message(f"Ping {host} PRE-reboot: {'OK' if ping_test(host) else 'FAIL'}")
        
    except Exception as e:
        log_message(f"Error on {host}: {e}")
        try:
            ssh.close()
        except:
            pass
    
    time.sleep(15)  # Pausa tra AP

def reboot_all():
    log_message("PING STATUS INIZIALE:")
    for ap in AP_LIST:
        log_message(f"  {ap['host']}: {'ONLINE' if ping_test(ap['host']) else 'OFFLINE'}")
    
    for ap in AP_LIST:
        reboot_ap(ap)
    
    log_message("=== MONITORAGGIO POST-REBOOT ===")
    time.sleep(120)  # Attendi 2min
    log_message("PING STATUS FINALE:")
    for ap in AP_LIST:
        status = 'ONLINE' if ping_test(ap['host']) else 'OFFLINE (riavvio completato?)'
        log_message(f"  {ap['host']}: {status}")

if __name__ == "__main__":
    reboot_all()
