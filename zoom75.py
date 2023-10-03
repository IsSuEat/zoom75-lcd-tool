import datetime
import hid

VENDOR_ID = 0x1EA7  # 7847
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
    devices = list(
        filter(lambda x: x["interface_number"] == 1, hid.enumerate(VENDOR_ID))
    )

    opened_devices = []
    for dev in devices:
        dev_path = dev["path"]
        print(f"opening device at path {dev_path}")
        try:
            h = hid.device()
            h.open_path(dev_path)
            h.set_nonblocking(1)
            opened_devices.append(h)
        except:
            print(f"failed to open device: {dev}")

    print(f"opened {len(opened_devices)} devices")
    return opened_devices


def set_cpu_temp(dev, temp):
    data = bytearray(32)
    data[8] = 0xA5
    data[9] = 0x37
    data[10] = 0x00
    data[11] = 0x03
    data[12] = 0x00
    data[13] = 0x00
    data[14] = temp
    data[15] = calc_checksum(data)

    data[0] = 0x1C
    data[5] = 0x08

    crc = crc16(data, 0, len(data))
    data[7] = (crc >> 8) & 0xFF
    data[6] = crc & 0xFF

    dev.write(data)


def set_gpu_temp(dev, temp):
    pass


def set_time(dev):
    now = datetime.datetime.now()
    data = bytearray(32)
    data[8] = 0xA5
    data[9] = 0x3F
    data[10] = 0x00
    data[11] = 0x0A
    data[12] = 0x00
    data[13] = 0x01

    data[14] = now.year >> 8
    data[15] = now.year & 0xFF
    data[16] = now.month
    data[17] = now.day
    data[18] = now.hour
    data[19] = now.minute
    data[20] = now.second
    data[21] = 0x01

    data[22] = calc_checksum(data)

    data[0] = 0x1C
    data[5] = 0x0F

    crc = crc16(data, 0, len(data))
    data[7] = (crc >> 8) & 0xFF
    data[6] = crc & 0xFF

    dev.write(data)


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
        set_time(dev)
        set_cpu_temp(dev, 42)
