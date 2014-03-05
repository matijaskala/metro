[collect ./source/stage3.spec]
[collect ./target/stage4.spec]
[collect ./steps/capture/livecd.spec]

[section stage4]

target/name: livecd

[section steps]

chroot/run: [
#!/bin/bash

emerge --oneshot $eopts portage || exit 1
export USE="$[portage/USE] bindist"
emerge -DNu $eopts @world || exit 1
emerge -DNu $eopts $[emerge/packages/force:zap] || exit 2
emerge -DNu $eopts $[emerge/packages:zap] || exit 1

KERNEL_PKGS="sys-kernel/genkernel-next $[livecd/kernel/package]"
echo > /etc/fstab || exit 1
ln -sf /proc/self/mounts /etc/mtab || exit 1
emerge $eopts --noreplace $KERNEL_PKGS || exit 1
echo "CONFIG_AUFS_FS=y" >> /usr/share/genkernel/arch/x86_64/kernel-config || exit 1
genkernel $[livecd/kernel/opts:lax] \
	--cachedir=/var/tmp/cache/kernel \
	--modulespackage=/var/tmp/cache/kernel/modules.tar.bz2 \
	--minkernpackage=/var/tmp/cache/kernel/kernel-initrd.tar.bz2 \
	all || exit 1

emerge -C $KERNEL_PKGS || exit 1
rm -rf /usr/src/linux-* /usr/src/linux || exit 1

echo 'hostname=livecd' > /etc/conf.d/hostname
hostnamectl set-hostname livecd

DISPLAYMANAGER=lxdm
systemctl enable $DISPLAYMANAGER
DISPLAYMANAGER_CONF="/etc/$DISPLAYMANAGER/$DISPLAYMANAGER.conf"
[ -f "$DISPLAYMANAGER_CONF" ] && sed -i s/\#\ autologin=dgod/autologin=liveuser/ $DISPLAYMANAGER_CONF
[ -f "/etc/init.d/xdm" ] && eselect rc add xdm
[ -f "/etc/conf.d/xdm" ] && sed -i s/\"xdm\"/\"$DISPLAYMANAGER\"/ /etc/conf.d/xdm

systemctl enable sshd
useradd -mp "" -G audio,disk,video,wheel liveuser
emerge --noreplace sudo syslinux || exit 1
echo "liveuser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
]
