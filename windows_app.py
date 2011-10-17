from win32gui import *
from win32con import *
from ctypes import *

def WinMain():
	# Define Window Class
	wndclass = WNDCLASS()
	wndclass.style = CS_HREDRAW | CS_VREDRAW
	wndclass.lpfnWndProc = WndProc
	wndclass.hInstance = GetModuleHandle(None)
	wndclass.hIcon = LoadIcon(None, IDI_APPLICATION)
	wndclass.hCursor = LoadCursor(None, IDC_ARROW)
	wndclass.hbrBackground = GetStockObject(WHITE_BRUSH)
	wndclass.lpszMenuName = ""
	wndclass.lpszClassName = "MainWin"
	# Register Window Class
	if not RegisterClass(wndclass):
		raise WinError()

	hwnd = CreateWindowEx(0,
						  wndclass.lpszClassName,
						  "Python Window",
						  WS_OVERLAPPEDWINDOW,
						  CW_USEDEFAULT,
						  CW_USEDEFAULT,
						  CW_USEDEFAULT,
						  CW_USEDEFAULT,
						  None,
						  None,
						  wndclass.hInstance,
						  None)
	# Show Window
	ShowWindow(hwnd, SW_SHOWNORMAL)
	UpdateWindow(hwnd)

	return PumpMessages() 

def WndProc(hwnd, message, wParam, lParam):
	
	if message == WM_PAINT:
		hdc , ps = BeginPaint(hwnd)
		rect = GetClientRect(hwnd)
		DrawText(hdc, "Python Powered Windows" ,
			-1, rect, 
			DT_SINGLELINE|DT_CENTER|DT_VCENTER)
			
		EndPaint(hwnd, ps)
		return 0
	elif message == WM_DESTROY:
		PostQuitMessage(0)
		return 0

	return DefWindowProc(hwnd, message, wParam, lParam)

WinMain()