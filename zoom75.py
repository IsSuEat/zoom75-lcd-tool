import datetime
import hid
import time

VENDOR_ID = 7847
PRODUCT_IDS = [52947, 52584, 52865]


def crc16(data: bytearray, offset, length):
    if (
        data is None
        or offset < 0
        or offset > len(data) - 1
        and offset + length > len(data)
    ):
        return 0
    crc = 0xFFFF
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for j in range(0, 8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF

def calc_checksum(data):
    return ((sum(data) & 0xFF) ^ 255) % 255 


def get_devices():
    for device_dict in hid.enumerate(VENDOR_ID):
        print(device_dict)

    opened_devices = []
    for id in PRODUCT_IDS:
        try:
            h = hid.device()
            # h.open(VENDOR_ID, id)
            # need to find the correct interface, for me this is 1
            h.open_path(b"5-2.1:1.1")  
            opened_devices.append(h)
        except Exception as e:
            print(f"failed to open device: {id}: {e}")

    print(f"opened {len(opened_devices)} devices")
    return opened_devices


def set_time(dev):
    now = datetime.datetime.now()
    num_array = bytearray(32)
    num_array[8] = 0xA5
    num_array[9] = 0x3F
    num_array[10] = 0
    num_array[11] = 0x0A
    num_array[12] = 0
    num_array[13] = 0x01
    num_array[14] = now.year >> 8
    num_array[15] = now.year & 0xFF
    num_array[16] = now.month
    num_array[17] = now.day
    num_array[18] = now.hour
    num_array[19] = now.minute
    num_array[20] = now.second
    num_array[21] = 1

    checksum = ((sum(num_array) & 0xFF) ^ 255) % 255 
    num_array[22] = calc_checksum(num_array)

    num_array[0] = 28
    num_array[5] = 15

    num = crc16(num_array, 0, len(num_array))
    num_array[7] = (num >> 8) & 0xFF
    num_array[6] = num & 0xFF

    res = dev.write(num_array)
    print(f"wrote {res}")
    


def send_known_good_data(dev):
    data = bytearray(32)
    data[0] = 0x1C
    data[5] = 0x0F
    data[6] = 0x37
    data[7] = 0xFE
    data[8] = 0xA5
    data[9] = 0x3F
    data[10] = 0x00
    data[11] = 0x0A
    data[12] = 0x00
    data[13] = 0x01
    data[14] = 0x07
    data[15] = 0xE7
    data[16] = 0x0A
    data[17] = 0x02
    data[18] = 0x17
    data[19] = 0x14
    data[20] = 0x19
    data[21] = 0x01
    data[22] = 0xD1
    data[23] = 0x00
    data[24] = 0x00
    data[25] = 0x00
    data[26] = 0x00
    data[27] = 0x00
    data[28] = 0x00
    data[29] = 0x00
    data[30] = 0x00
    data[31] = 0x00
    dev.write(data)


if __name__ == "__main__":
    devs = get_devices()
   
    for dev in devs:
        dev.set_nonblocking(1)
        set_time(dev)
