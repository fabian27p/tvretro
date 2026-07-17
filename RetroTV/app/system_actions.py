from __future__ import annotations
import shutil,subprocess
from datetime import datetime

def update_clock():
    if not shutil.which('timedatectl'):
        return False,'HORA\nNo existe timedatectl en este sistema'
    cmds=[
        ['timedatectl','set-ntp','true'],
        ['systemctl','restart','systemd-timesyncd'],
    ]
    for cmd in cmds:
        try: subprocess.run(cmd,check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=8)
        except Exception: pass
    try:
        out=subprocess.check_output(['timedatectl','show','-p','NTPSynchronized','--value'],text=True,timeout=5).strip()
        ok=out.lower()=='yes'
    except Exception:
        ok=False
    now=datetime.now().strftime('%H:%M %d-%m-%Y')
    return ok,('HORA ACTUALIZADA\n' if ok else 'HORA\nSin confirmacion NTP\n')+now

def set_manual_clock(clock):
    try:
        dt=datetime(int(clock['year']),int(clock['month']),int(clock['day']),int(clock['hour']),int(clock['minute']))
    except Exception:
        return False,'HORA MANUAL\nFecha invalida'
    value=dt.strftime('%Y-%m-%d %H:%M:%S')
    if not shutil.which('timedatectl'):
        return False,'HORA MANUAL\nNo existe timedatectl\n'+dt.strftime('%H:%M %d-%m-%Y')
    try:
        subprocess.run(['timedatectl','set-ntp','false'],check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5)
        r=subprocess.run(['timedatectl','set-time',value],check=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=8)
        ok=r.returncode==0
    except Exception:
        ok=False
    return ok,('HORA CONFIGURADA\n' if ok else 'HORA MANUAL\nNo se pudo aplicar\n')+dt.strftime('%H:%M %d-%m-%Y')
