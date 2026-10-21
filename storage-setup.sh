#!/usr/bin/env bash
set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "Запустите скрипт через sudo." >&2
  exit 1
fi

for command_name in losetup mdadm pvcreate vgcreate lvcreate mkfs.ext4 mount; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Не найдена команда: $command_name" >&2
    exit 1
  fi
done

LAB_DIR=/mnt/raid-lab
mkdir -p "$LAB_DIR" /mnt/raid /mnt/logs

create_disk_image() {
  image_path=$1
  if [ ! -f "$image_path" ]; then
    dd if=/dev/zero of="$image_path" bs=1M count=512 status=none
  fi
}

attach_image() {
  image_path=$1
  existing_loop=$(losetup -j "$image_path" | head -1 | cut -d: -f1)
  if [ -n "$existing_loop" ]; then
    printf '%s\n' "$existing_loop"
  else
    losetup -fP --show "$image_path"
  fi
}

create_disk_image "$LAB_DIR/disk1.img"
create_disk_image "$LAB_DIR/disk2.img"
create_disk_image "$LAB_DIR/disk3.img"

LOOP1=$(attach_image "$LAB_DIR/disk1.img")
LOOP2=$(attach_image "$LAB_DIR/disk2.img")
LOOP3=$(attach_image "$LAB_DIR/disk3.img")

if [ ! -e /dev/md0 ]; then
  yes | mdadm --create /dev/md0 --level=1 --raid-devices=2 --force "$LOOP1" "$LOOP2"
fi
mdadm --wait /dev/md0 || true

if ! blkid /dev/md0 >/dev/null 2>&1; then
  mkfs.ext4 -F /dev/md0
fi
if ! findmnt /mnt/raid >/dev/null 2>&1; then
  mount /dev/md0 /mnt/raid
fi

if ! pvs "$LOOP3" >/dev/null 2>&1; then
  pvcreate -ff -y "$LOOP3"
fi
if ! vgs vg_data >/dev/null 2>&1; then
  vgcreate vg_data "$LOOP3"
fi
if ! lvs vg_data/lv_logs >/dev/null 2>&1; then
  lvcreate -y -L 200M -n lv_logs vg_data
fi

if ! blkid /dev/vg_data/lv_logs >/dev/null 2>&1; then
  mkfs.ext4 -F /dev/vg_data/lv_logs
fi
if ! findmnt /mnt/logs >/dev/null 2>&1; then
  mount /dev/vg_data/lv_logs /mnt/logs
fi

chmod 0775 /mnt/logs
if [ -n "${SUDO_USER:-}" ] && [ "$SUDO_USER" != root ]; then
  chown "$SUDO_USER":"$SUDO_USER" /mnt/logs
fi

echo "RAID 1 и LVM готовы."
cat /proc/mdstat
pvs
vgs
lvs
df -h /mnt/raid /mnt/logs
