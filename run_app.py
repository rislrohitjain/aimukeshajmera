import socket
import webbrowser
import os
import sys
import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_all_ip_addresses():
    """Returns a list of all active IPv4 addresses on this machine."""
    ip_list = ["127.0.0.1"]
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127.") and ip not in ip_list:
                ip_list.append(ip)
    except Exception:
        pass
    return ip_list

def ensure_database():
    """Checks and creates PostgreSQL database 'aimukeshajmera' if missing."""
    db_name = "aimukeshajmera"
    user = "postgres"
    password = "Admin@123"
    host = "localhost"
    port = 5432
    
    print(f"[*] Checking PostgreSQL connection on {host}:{port}...")
    try:
        conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        if not exists:
            print(f"[*] Creating PostgreSQL database '{db_name}'...")
            cur.execute(f"CREATE DATABASE {db_name}")
            print(f"[OK] Database '{db_name}' created successfully!")
        else:
            print(f"[OK] Database '{db_name}' is ready.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[!] Warning checking database: {e}")

if __name__ == "__main__":
    print("\n=======================================================")
    print("  MUKESH AJMERA LIC & POST OFFICE SERVICES - SARWAR   ")
    print("=======================================================\n")
    
    ensure_database()
    
    port = 5050
    ip_addresses = get_all_ip_addresses()
    primary_url = f"http://localhost:{port}"

    print("\n-------------------------------------------------------")
    print(f"  * Primary URL (Recommended): {primary_url}")
    print(f"  * Local Network Access URLs :")
    for ip in ip_addresses:
        print(f"     -> http://{ip}:{port}")
    print("  * Admin Credentials        : Phone: 9829943216 | Pass: 9829943216")
    print("-------------------------------------------------------\n")
    print("[*] Opening web browser at http://localhost:5050 in 1.5 seconds...")

    # Automatically open primary localhost URL in default browser
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(primary_url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    from app import create_app
    app = create_app()
    
    # Run on 0.0.0.0 so server listens on all network adapters
    app.run(host="0.0.0.0", port=port, debug=False)
