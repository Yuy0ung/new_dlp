from ctypes import *
import sys
import _thread
import win32serviceutil
import win32service
import win32con
import sqlite3
import os
import threading
from plugin.config.config import cfg
from PyQt5.QtCore import QModelIndex, Qt,QThreadPool,QThread,QRunnable,pyqtSignal,QObject
def manage_service(service_name, action):
    """通过 win32service 控制服务"""
    try:
        if action == "start":
            win32serviceutil.StartService(service_name)
        elif action == "stop":
            win32serviceutil.StopService(service_name)
        elif action == "restart":
            win32serviceutil.RestartService(service_name)
        
        # 获取服务状态
        status = win32serviceutil.QueryServiceStatus(service_name)[1]
        state = {
            win32service.SERVICE_STOPPED: "已停止",
            win32service.SERVICE_RUNNING: "运行中",
            win32service.SERVICE_PAUSED: "已暂停",
        }.get(status, "未知状态")
        print(f"服务状态：{state}")
    except Exception as e:
        print(f"操作失败：{str(e)}")
        raise e
# def LoadDll():
#     try:
#         global lib,ServerClass
#         lib= cdll.LoadLibrary(r'plugin\protection\Dll_minifilter.dll')
#         lib.GetClass.argtypes =[]
#         lib.GetClass.restype=c_void_p
#         ServerClass=lib.GetClass()
#     except Exception as e:
#         raise e
#     print("dll加载成功")
# def StartServer():
#     global ServerThread
#     lib.ServerRunner.argtypes =[c_void_p]
#     lib.ServerRunner.restype=None
#     lib.StartServer.argtypes =[c_void_p]
#     lib.StartServer.restype=None
#     lib.StartServer(ServerClass)
#     ServerThread=threading.Thread(target=lib.ServerRunner,args=(ServerClass,))
#     ServerThread.start()
#     print(f"服务器启动成功 alive:{ServerThread.is_alive()}")
# def StopServer():
    # lib.StopServer.argtypes =[c_void_p]
    # lib.StopServer.restype =None
    # lib.StopServer(ServerClass)
def get_dos_drives():
    """获取所有逻辑驱动器的盘符"""
    buffer_size = windll.kernel32.GetLogicalDriveStringsW(0, None)
    if buffer_size == 0:
        return []
    buffer = create_unicode_buffer(buffer_size)
    if windll.kernel32.GetLogicalDriveStringsW(buffer_size, buffer) == 0:
        return []
    drives = ''.join(buffer).split('\x00')[:-2]  # 分割并去除末尾的空字符串
    return [drive[:2] for drive in drives]  # 提取盘符（如"C:"）
def is_parent_directory(child_path, parent_path):
    # 将路径转换为绝对路径
    child_abspath = os.path.abspath((NtDict[child_path[:23]]+child_path[23:]).replace('\\',"/"))
    parent_abspath = os.path.abspath(parent_path)
    
    # 判断parent_path是否是child_path的父目录
    return os.path.commonpath([child_abspath]) == os.path.commonpath([child_abspath, parent_abspath]) and child_abspath != parent_abspath
def get_nt_device_mapping():
    """建立DOS设备路径到NT盘符的映射"""
    global mapping
    mapping = {}
    for drive in get_dos_drives():
        buf = create_unicode_buffer(1024)
        if windll.kernel32.QueryDosDeviceW(drive, buf, 1024) == 0:
            continue
        nt_path = buf.value
        # 统一使用小写并标准化路径分隔符
        mapping[drive.upper()] = nt_path
    return mapping

protectiondb=None
dbDir=os.path.join(cfg.tempDir.value,"protection.db")
DosDict=get_nt_device_mapping()
NtDict={value: key for key, value in DosDict.items()}
if os.path.exists(dbDir):
    protectiondb =sqlite3.connect(dbDir, timeout=10, check_same_thread=False,isolation_level= "IMMEDIATE")
else:
    protectiondb = sqlite3.connect(dbDir, timeout=10, check_same_thread=False,isolation_level= "IMMEDIATE")
    dbcursor = protectiondb.cursor()
    try:
        create_table = '''
        CREATE TABLE protections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullpath TEXT
        );
        '''
        dbcursor.execute(create_table)

        protectiondb.commit()
        dbcursor = protectiondb.cursor()
    except Exception as e:
        print(e)
        pass


class ProtectionSignals(QObject):
    UnknownEnd=pyqtSignal(bool)
    reject=pyqtSignal(str)
class Protection(QRunnable):
    def __init__(self):
        super().__init__()
        self.stoped=False
        self.signals=ProtectionSignals()
        try:
            self.lib= cdll.LoadLibrary(r'resource\minifilter\Dll_minifilter.dll')
            self.lib.GetClass.argtypes =[]
            self.lib.GetClass.restype=c_void_p
            self.lib.ServerRunner.argtypes =[c_void_p]
            self.lib.ServerRunner.restype=None
            self.lib.StartServer.argtypes =[c_void_p]
            self.lib.StartServer.restype=None
            self.ServerClass=self.lib.GetClass()
        except Exception as e:
            raise e
        
    def run(self):
        self.lib.StartServer(self.ServerClass)
        self.RegistProtection()
        try:
            self.lib.ServerRunner(self.ServerClass)
        except Exception as e:
            self.signals.UnknownEnd.emit(True)
        if not self.stoped:
            self.signals.UnknownEnd.emit(True)
    def stop(self):
        self.StopServer()
        self.stoped=True
        self.signals.UnknownEnd.emit(False)
    def RegistProtection(self):
        # 定义回调类型
        CallbackType = CFUNCTYPE(
            c_int,                # 返回值类型
            c_void_p, c_size_t,   # buffer, buffer_len
            c_void_p, c_size_t    # response, response_len
        )
        # Python回调实现
        # 将Python函数转换为C回调
        global callback
        callback = CallbackType(self.py_callback)

        # 注册回调
        self.lib.AddCallback.argtypes = [c_void_p,CallbackType]
        self.lib.AddCallback.restype = None
        self.lib.AddCallback(self.ServerClass,callback)
        print("回调注册成功")
        return True    
    def StopServer(self):
        self.lib.StopServer.argtypes =[c_void_p]
        self.lib.StopServer.restype =None
        self.lib.StopServer(self.ServerClass)
    def py_callback(self,buffer, buffer_len, response, response_len):
            # 读取输入数据
            if buffer_len==0:
                return 0
            # print( bytes((c_wchar * (buffer_len//2)).from_address(buffer)))
            input_data = bytes((c_wchar * (buffer_len//2)).from_address(buffer)).decode().replace("\x00", "")#将wchar转为普通字符串
            #此处一调用sqlite3就会卡死 注意
            def sendText(input):
                output_data=b"no"
                try:
                    for i in cfg.blackFolders.value:
                        if is_parent_directory(input,i):
                            output=b"yes"
                            break
                    else:
                        for i in cfg.whiteFolders.value:
                            if is_parent_directory(input,i):
                                break
                        else:
                            output=protectiondb.execute("SELECT * FROM protections WHERE fullpath = ?",(input,)).fetchone()
                    if output:
                        self.signals.reject.emit(input_data)
                        output_data=b"yes"
                except Exception as e:
                    print(str(e))
                finally:
                    memmove(response, output_data, 2)     

            t=threading.Thread(target=sendText,args=(input_data,))
            t.start()
            t.join()
            # 返回状态码（假设0表示成功）
            return 1    
