import os
import sys
import time
import ctypes
import psutil

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("[-] Для точного анализа сети запустите агент ОТ ИМЕНИ АДМИНИСТРАТОРА!")
    input("\nНажмите Enter для выхода...")
    sys.exit()

# Списки для анализа
REMOTE_TOOLS = ["anydesk", "teamviewer", "rustdesk", "ultraviewer", "vnc", "radmin", "ammyy"]
SYSTEM_WHITE_LIST = ["svchost.exe", "system", "lsass.exe", "dashost.exe", "explorer.exe", "spoolsv.exe"]
BROWSER_WHITE_LIST = ["chrome.exe", "msedge.exe", "browser.exe", "firefox.exe", "opera.exe"]

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

print("[*] Инициализация защитного агента Cyber Puls...")
time.sleep(1)

try:
    while True:
        clear_console()
        print("="*70)
        print(" [Cyber Puls] МОНИТОРИНГ БЕЗОПАСНОСТИ СИСТЕМЫ В РЕАЛЬНОМ ВРЕМЕНИ")
        print("="*70)
        
        alerts = []
        remote_detected = []
        active_connections = 0
        
        # 1. Проверка сетевых подключений
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    active_connections += 1
                    pid = conn.pid
                    if pid:
                        try:
                            proc = psutil.Process(pid)
                            p_name = proc.name().lower()
                            
                            # Игнорируем доверенные системные процессы и браузеры
                            if p_name in SYSTEM_WHITE_LIST or p_name in BROWSER_WHITE_LIST:
                                continue
                                
                            alerts.append(f"  [СЕТЬ] Программа '{proc.name()}' (PID: {pid}) держит активное соединение с {conn.laddr.ip} -> {conn.raddr.ip}")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
        except Exception as e:
            alerts.append(f"  [СБОЙ] Ошибка сканирования сети: {e}")

        # 2. Проверка запущенных процессов удаленного доступа
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                p_name = proc.info['name'].lower()
                if any(tool in p_name for tool in REMOTE_TOOLS):
                    remote_detected.append(f"  [УДАЛЕННЫЙ ДОСТУП] Обнаружена запущенная утилита управления: {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # 3. Вывод статуса безопасности
        if not alerts and not remote_detected:
            # ЗЕЛЕНЫЙ СТАТУС (Угроз нет)
            print("\n STATUS: [ БЕЗОПАСНО ] ")
            print(" -> Внешнее управление не обнаружено.")
            print(f" -> Активных сетевых сессий под контролем: {active_connections}")
            print("\n Агент работает в фоновом режиме. Ноутбук защищен.")
        else:
            # ЖЕЛТЫЙ/КРАСНЫЙ СТАТУС (Есть подозрительная активность)
            print("\n STATUS: [ ВНИМАНИЕ / ОБНАРУЖЕНА АКТИВНОСТЬ ] ")
            print(" -> Система зафиксировала нетипичные процессы или соединения:")
            
            if remote_detected:
                print("\n[!] АКТИВНЫЙ ИНСТРУМЕНТ УДAЛЕННОГО ДОСТУПА:")
                for rd in remote_detected:
                    print(rd)
                    
            if alerts:
                print("\n[!] ПОДОЗРИТЕЛЬНЫЕ СЕТЕВЫЕ ПОДКЛЮЧЕНИЯ:")
                for al in alerts:
                    print(al)
                    
            print("\n РЕКОМЕНДАЦИЯ: Если вы не запускали эти программы сами, отключите интернет и завершите данные процессы через Диспетчер задач.")

        print("\n" + "="*70)
        print(" Для выхода нажмите Ctrl + C | Обновление каждые 4 секунды...")
        
        # Задержка в 4 секунды, чтобы вообще не нагружать процессор Celeron
        time.sleep(4)

except KeyboardInterrupt:
    print("\n[-] Мониторинг остановлен пользователем.")

