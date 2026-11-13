"""Small, portable context features shared by capture and retrieval nodes."""
from sensor_msgs.msg import LaserScan


def scan_signature(scan: LaserScan, sectors: int = 24) -> tuple[float, ...]:
    """Compress a scan into per-sector minima without retaining raw sensor data."""
    if not scan.ranges:
        return ()
    sectors = max(1, sectors)
    size = max(1, len(scan.ranges) // sectors)
    signature = []
    for index in range(sectors):
        values = [value for value in scan.ranges[index * size:(index + 1) * size]
                  if scan.range_min <= value <= scan.range_max]
        signature.append(min(values) if values else scan.range_max)
    return tuple(signature)
