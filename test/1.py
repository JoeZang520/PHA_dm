import ctypes
import win32com.client

obj = ctypes.windll.LoadLibrary(r"C:\Users\J9\Desktop\PHA_dm\DmReg.dll")
obj.SetDllPathW(r"C:\Users\J9\Desktop\PHA_dm\dm.dll")

dm = win32com.client.Dispatch('dm.dmsoft')

print(dm.ver())

res = dm.reg("mh84909b3bf80d45c618136887775ccc90d27d7", "mimhwsaelcfp20vf7")
print(res)

hwnd= 4525184
res = dm.BindWindow(hwnd, "normal", "windows2", "windows", 0)
print(res)


dm.moveto(407,738)
dm.leftclick()

dm.keydown(0x53)


