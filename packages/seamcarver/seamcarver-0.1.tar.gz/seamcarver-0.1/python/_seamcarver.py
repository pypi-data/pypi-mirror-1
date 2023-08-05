from ctypes import *

_libraries = {}
_libraries['libseamcarver.so'] = CDLL('libseamcarver.so')


class seamcarver_struct(Structure):
    pass
seamcarver_t = POINTER(seamcarver_struct)
seamcarver_struct._fields_ = [
]
seamcarver_new = _libraries['libseamcarver.so'].seamcarver_new
seamcarver_new.restype = seamcarver_t
seamcarver_new.argtypes = [POINTER(c_ubyte), c_int, c_int, c_int]
seamcarver_free = _libraries['libseamcarver.so'].seamcarver_free
seamcarver_free.restype = None
seamcarver_free.argtypes = [seamcarver_t]
seamcarver_get_rgb_data = _libraries['libseamcarver.so'].seamcarver_get_rgb_data
seamcarver_get_rgb_data.restype = POINTER(c_ubyte)
seamcarver_get_rgb_data.argtypes = [seamcarver_t]
seamcarver_get_energy_data = _libraries['libseamcarver.so'].seamcarver_get_energy_data
seamcarver_get_energy_data.restype = POINTER(c_ubyte)
seamcarver_get_energy_data.argtypes = [seamcarver_t]
seamcarver_retarget = _libraries['libseamcarver.so'].seamcarver_retarget
seamcarver_retarget.restype = POINTER(c_ubyte)
seamcarver_retarget.argtypes = [seamcarver_t, c_int, c_int]
__all__ = ['seamcarver_new', 'seamcarver_retarget',
           'seamcarver_get_energy_data', 'seamcarver_struct',
           'seamcarver_free', 'seamcarver_get_rgb_data',
           'seamcarver_t']
