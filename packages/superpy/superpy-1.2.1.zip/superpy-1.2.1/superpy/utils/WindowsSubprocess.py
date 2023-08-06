"""Module providing ways to spawn subprocess on windows.

This module is designed to simplify the process of spawning processes
on windows machines by calling CreateProcessWithLogonW.
"""

import ctypes, win32api

NULL  = 0
TRUE  = 1
FALSE = 0

INVALID_HANDLE_VALUE = -1
CREATE_DEFAULT_ERROR_MODE = 0x04000000
DETACHED_PROCESS = 0x00000008

WORD   = ctypes.c_ushort
DWORD  = ctypes.c_uint
LPSTR  = ctypes.c_char_p
LPBYTE = LPSTR
HANDLE = DWORD

# typedef struct _PROCESS_INFORMATION {
#     HANDLE hProcess;
#     HANDLE hThread;
#     DWORD dwProcessId;
#     DWORD dwThreadId;
# } PROCESS_INFORMATION, *PPROCESS_INFORMATION, *LPPROCESS_INFORMATION;
class PROCESS_INFORMATION(ctypes.Structure):
    """Class representing PROCESS_INFORMATION structure in c.
    """
    _pack_   = 1
    _fields_ = [
        ('hProcess',    HANDLE),
        ('hThread',     HANDLE),
        ('dwProcessId', DWORD),
        ('dwThreadId',  DWORD),
        ]

# typedef struct _STARTUPINFO {
#     DWORD   cb;
#     LPSTR   lpReserved;
#     LPSTR   lpDesktop;
#     LPSTR   lpTitle;
#     DWORD   dwX;
#     DWORD   dwY;
#     DWORD   dwXSize;
#     DWORD   dwYSize;
#     DWORD   dwXCountChars;
#     DWORD   dwYCountChars;
#     DWORD   dwFillAttribute;
#     DWORD   dwFlags;
#     WORD    wShowWindow;
#     WORD    cbReserved2;
#     LPBYTE  lpReserved2;
#     HANDLE  hStdInput;
#     HANDLE  hStdOutput;
#     HANDLE  hStdError;
# } STARTUPINFO, *LPSTARTUPINFO;
class STARTUPINFO(ctypes.Structure):
    """Python class representing C STARTUPINFO class.
    """
    _pack_   = 1
    _fields_ = [
        ('cb',              DWORD),
        ('lpReserved',      DWORD),     # LPSTR
        ('lpDesktop',       LPSTR),
        ('lpTitle',         LPSTR),
        ('dwX',             DWORD),
        ('dwY',             DWORD),
        ('dwXSize',         DWORD),
        ('dwYSize',         DWORD),
        ('dwXCountChars',   DWORD),
        ('dwYCountChars',   DWORD),
        ('dwFillAttribute', DWORD),
        ('dwFlags',         DWORD),
        ('wShowWindow',     WORD),
        ('cbReserved2',     WORD),
        ('lpReserved2',     DWORD),     # LPBYTE
        ('hStdInput',       DWORD),
        ('hStdOutput',      DWORD),
        ('hStdError',       DWORD),
        ]

# BOOL WINAPI CreateProcessWithLogonW(
#   __in         LPCWSTR lpUsername,
#   __in_opt     LPCWSTR lpDomain,
#   __in         LPCWSTR lpPassword,
#   __in         DWORD dwLogonFlags,
#   __in_opt     LPCWSTR lpApplicationName,
#   __inout_opt  LPWSTR lpCommandLine,
#   __in         DWORD dwCreationFlags,
#   __in_opt     LPVOID lpEnvironment,
#   __in_opt     LPCWSTR lpCurrentDirectory,
#   __in         LPSTARTUPINFOW lpStartupInfo,
#   __out        LPPROCESS_INFORMATION lpProcessInfo
# );

def CreateProcessWithLogonW(
    lpUsername = None, lpDomain = None, lpPassword = None, dwLogonFlags = 0,
    lpApplicationName = None, lpCommandLine = None, dwCreationFlags = 0,
    lpEnvironment = None, lpCurrentDirectory = None, lpStartupInfo = None):
    """Create a new process with given logon.
    
    INPUTS:
    
    -- lpUsername=None:        Username for new process.
    
    -- lpDomain=None:          String domain for new process.
    
    -- lpPassword=None:        String password for new process.
    
    -- dwLogonFlags=0:         Integer representing logon flags for new
                               process.
    
    -- lpApplicationName=None: String application name.       
    
    -- lpCommandLine=None:     String command line for process.   
    
    -- dwCreationFlags=0:      Flags for creating new process.  
    
    -- lpEnvironment=None:     Envionmnet block for new process. Tricky to use.
    
    -- lpCurrentDirectory=None:  String directory to start in.      
    
    -- lpStartupInfo=None:     Startup info structure for new process.   
    
    -------------------------------------------------------
    
    RETURNS:  PROCESS_INFORMATION structure for new process.
    
    -------------------------------------------------------
    
    PURPOSE:  Create a new process for the given user.
    
    """

    lpUsername = ctypes.c_wchar_p(lpUsername) if lpUsername else NULL
    lpDomain = ctypes.c_wchar_p(lpDomain) if lpDomain else NULL
    lpPassword = ctypes.c_wchar_p(lpPassword) if lpPassword else NULL
    lpApplicationName = (ctypes.c_wchar_p(lpApplicationName)
                         if lpApplicationName else NULL)
    lpCommandLine = (ctypes.create_unicode_buffer(lpCommandLine)
                     if lpCommandLine else NULL)
    lpEnvironment = ctypes.c_wchar_p(lpEnvironment) if lpEnvironment else NULL
    lpCurrentDirectory = (ctypes.c_wchar_p(lpCurrentDirectory)
                          if (lpCurrentDirectory) else NULL)
    if not lpStartupInfo:    
        lpStartupInfo = MakeStartupInfo()
    lpProcessInformation              = PROCESS_INFORMATION()
    lpProcessInformation.hProcess     = INVALID_HANDLE_VALUE
    lpProcessInformation.hThread      = INVALID_HANDLE_VALUE
    lpProcessInformation.dwProcessId  = 0
    lpProcessInformation.dwThreadId   = 0
    success = ctypes.windll.advapi32.CreateProcessWithLogonW(
        lpUsername, lpDomain, lpPassword, dwLogonFlags, lpApplicationName,
        ctypes.byref(lpCommandLine), ctypes.c_uint(dwCreationFlags),
        lpEnvironment, lpCurrentDirectory, ctypes.byref(lpStartupInfo),
        ctypes.byref(lpProcessInformation))
    if success == FALSE:
        raise ctypes.WinError()
    return lpProcessInformation

def MakeStartupInfo():
    """Make STARTUPINFO structure.
    """

    lpStartupInfo              = STARTUPINFO()
    lpStartupInfo.cb           = ctypes.sizeof(STARTUPINFO)
    lpStartupInfo.lpReserved   = 0
    lpStartupInfo.lpDesktop    = 0
    lpStartupInfo.lpTitle      = 0
    lpStartupInfo.dwFlags      = 0
    lpStartupInfo.cbReserved2  = 0
    lpStartupInfo.lpReserved2  = 0
    lpStartupInfo.hStdInput = win32api.GetStdHandle(win32api.STD_INPUT_HANDLE)
    lpStartupInfo.hStdOutput = win32api.GetStdHandle(win32api.STD_OUTPUT_HANDLE)
    lpStartupInfo.hStdError = win32api.GetStdHandle(win32api.STD_ERROR_HANDLE)

    return lpStartupInfo


def _regr_test():
    """
>>> import WindowsSubprocess
>>> from logging import info
>>> info('''Could test this via something like
... p = WindowsSubprocess.CreateProcessWithLogonW(
... lpUsername=<username>, lpDomain=<domain>, lpPassword=<password>,
... lpApplicationName='C:\\Python25\python.exe',
... lpCommandLine='C:\\Python25\python25.exe -i')
... ''')

    """


def _test():
    "Test docstrings in module."
    import doctest
    doctest.testmod()

if __name__ == "__main__":    
    _test()
    print 'Test finished.'
            
