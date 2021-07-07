from codecs import decode
import struct
import ast

# def convert_imu_register_value(sign, high_byte, low_byte):
#     unsigned_value = (256*high_byte + low_byte)
#     if sign == 1:
#         unsigned_value *= -1
#     return unsigned_value

def convert_imu_reg_values_to_float(reg_values):
    binary = convert_imu_reg_values_to_binary(reg_values)
    return convert_binary_to_float(binary)

def convert_imu_reg_values_to_binary(reg_values):
    binary = reg_values[3]*(2**24) + reg_values[2]*(2**16)+ reg_values[1]*(2**8)+ reg_values[0]
    return binary

def convert_binary_to_float(binary):
    binary_string = bin(binary)[2:]
    num_float = int(binary_string, 2)
    return struct.unpack('f', struct.pack('I', num_float))[0]
