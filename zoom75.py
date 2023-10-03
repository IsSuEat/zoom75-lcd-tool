import datetime
import time
import hid
import psutil
import math
import argparse

VENDOR_ID = 0x1EA7
PRODUCT_ID = 0xCED3


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
        filter(
            lambda x: x["interface_number"] == 1, hid.enumerate(VENDOR_ID, PRODUCT_ID)
        )
    )

    if len(devices) == 0:
        raise ValueError(
            f"no device found matching vendor id: {VENDOR_ID} product id: {PRODUCT_ID}"
        )

    opened_devices = []
    for dev in devices:
        dev_path = dev["path"]
        print(f"opening device at path {dev_path}")

        h = hid.device()
        try:
            h.open_path(dev_path)
            h.set_nonblocking(1)
            opened_devices.append(h)
        except Exception as e:
            print(f"failed to open device: {dev}: {e}")

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
    data = bytearray(32)
    data[8] = 0xA5
    data[9] = 0x38
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


def set_fan_speed(dev, speed):
    data = bytearray(32)

    data[8] = 0xA5
    data[9] = 0x39
    data[10] = 0x00
    data[11] = 0x03
    data[12] = 0x00
    data[13] = (speed >> 8) & 0xFF
    data[14] = speed & 0xFF
    data[15] = calc_checksum(data)

    data[0] = 0x1C
    data[5] = 0x08

    crc = crc16(data, 0, len(data))
    data[7] = (crc >> 8) & 0xFF
    data[6] = crc & 0xFF

    dev.write(data)


def set_net_speed(dev, speed):
    data = bytearray(32)

    data[8] = 0xA5
    data[9] = 0x3D
    data[10] = 0x00
    data[11] = 0x05
    data[12] = 0x00
    data[13] = (((speed >> 8) >> 8) >> 8) & 0xFF
    data[14] = ((speed >> 8) >> 8) & 0xFF
    data[15] = (speed >> 8) & 0xFF
    data[16] = speed & 0xFF
    data[17] = calc_checksum(data)

    data[0] = 0x1C
    data[5] = 0x08

    crc = crc16(data, 0, len(data))
    data[7] = (crc >> 8) & 0xFF
    data[6] = crc & 0xFF

    dev.write(data)


def set_weather(dev):
    code = 5
    weather1 = 13
    weather2 = 37

    data = bytearray(32)

    data[8] = 0xA5
    data[9] = 0x3B
    data[10] = 0x00
    data[11] = 0x04
    data[12] = 0x00
    data[13] = code
    data[14] = weather1 & 0xFF
    data[15] = weather2 & 0xFF
    data[16] = calc_checksum(data)

    data[0] = 0x1C
    data[5] = 0x09

    crc = crc16(data, 0, len(data))
    data[7] = (crc >> 8) & 0xFF
    data[6] = crc & 0xFF

    dev.write(data)


def query_sensors(cputemp_module, cputemp_label, gputemp_module, gputemp_label):
    all_sensors = psutil.sensors_temperatures()

    cpu_sensors = all_sensors[cputemp_module]
    cpu_sensor = list(filter(lambda x: x.label == cputemp_label, cpu_sensors))

    if len(cpu_sensor) != 1:
        raise ValueError("failed to get cpu temp")

    gpu_sensors = all_sensors[gputemp_module]
    gpu_sensor = list(filter(lambda x: x.label == gputemp_label, gpu_sensors))

    if len(gpu_sensor) != 1:
        raise ValueError("failed to get gpu temp")

    current_cpu_temp = math.floor(cpu_sensor[0].current)
    current_gpu_temp = math.floor(gpu_sensor[0].current)

    # TODO
    current_rpm = 0
    current_netspeed = 0

    return (current_cpu_temp, current_gpu_temp, current_rpm, current_netspeed)


def background(args):
    devs = get_devices()
    while True:
        cpu_temp, gpu_temp, rpm, netspeed = query_sensors(
            args.cputemp_module,
            args.cputemp_label,
            args.gputemp_module,
            args.gputemp_label,
        )

        for dev in devs:
            set_cpu_temp(dev, cpu_temp)
            set_gpu_temp(dev, gpu_temp)
            # set_fan_speed(dev, rpm)
            # set_net_speed(dev, netspeed)

        time.sleep(1)


def main():
    arg_parser = argparse.ArgumentParser(
        prog="zoom75 LCD tool",
        description="Set and update information on the zoom75 LCD kit on Linux",
    )

    sub_parsers = arg_parser.add_subparsers(dest="command", help="Subcommand help")

    keep_alive_parser = sub_parsers.add_parser(
        "keep-alive",
        help="Keep the tool running to continuously update temperature readings",
    )
    keep_alive_parser.add_argument(
        "--cputemp-module",
        help="Name of the module used for cpu temperature, e.g. k10temp",
    )
    keep_alive_parser.add_argument(
        "--cputemp-label",
        help="Label of the sensor used to read cpu temperature, e.g. Tctl",
    )
    keep_alive_parser.add_argument(
        "--gputemp-module",
        help="Name of the module used for gpu temperature, e.g. amdgpu",
    )
    keep_alive_parser.add_argument(
        "--gputemp-label",
        help="Label of the sensor used to read gpu temperature, e.g. junction",
    )

    oneshot_parser = sub_parsers.add_parser("oneshot", help="Update a single value once")
    oneshot_parser.add_argument(
        "-t",
        "--set-date-time",
        action="store_true",
        help="Set time and date to the current date/time",
    )

    args = arg_parser.parse_args()

    if args.command == "keep-alive":
        try:
            background(args)
        except KeyboardInterrupt:
            print("exiting")
            exit(0)
    elif args.command == "oneshot":
        devs = get_devices()
        for dev in devs:
            if args.set_date_time:
                set_time(dev)
    else:
        arg_parser.print_help()


if __name__ == "__main__":
    main()
