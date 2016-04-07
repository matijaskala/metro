[collect ./source/stage2.spec]
[collect ./target/stage3.spec]
[collect ./steps/capture/tar.spec]

[section steps]

chroot/run: [
#!/bin/bash
$[[steps/setup]]

# use python2 if available - if not available, assume we are OK with python3
a=$(eselect python list | sed -n -e '1d' -e 's/^.* \(python[23]\..\).*$/\1/g' -e '/python2/p')
# if python2 is available, "$a" should be set to something like "python2.6":
if [ "$a" != "" ]
then
	eselect python set $a
fi

emerge $eopts portage || exit 1
USE="-*" emerge $eopts pambase || exit 1
export USE="$[portage/USE] bindist"
# handle perl upgrades
perl-cleaner --modules || exit 1
emerge $eopts -e system || exit 1

emerge $eopts $[emerge/packages/first:zap] || exit 1
echo "media-gfx/blender ~$[target/arch]" >> /etc/portage/package.accept_keywords
echo "net-im/pidgin ~$[target/arch]" >> /etc/portage/package.accept_keywords
echo "net-libs/webkit-gtk ~$[target/arch]" >> /etc/portage/package.accept_keywords
echo "=sci-libs/ldl-2.1.0 ~$[target/arch]" >> /etc/portage/package.accept_keywords
echo "sys-apps/shadow ~$[target/arch]" >> /etc/portage/package.accept_keywords
echo "www-client/google-chrome ~$[target/arch]" >> /etc/portage/package.accept_keywords
echo "www-client/midori ~$[target/arch]" >> /etc/portage/package.accept_keywords
emerge $eopts "sys-apps/shadow"

# zap the world file and emerge packages
rm -f /var/lib/portage/world || exit 2

emerge $eopts $[emerge/packages:zap] || exit 1

# add default runlevel services
services=""
services="$[baselayout/services:zap]"

for service in $services
do
	s=${service%%:*}
	l=${service##*:}
	[ "$l" == "$s" ] && l="default"
	rc-update add $s ${l}
done

if [ -e /usr/share/eselect/modules/vi.eselect ] && [ -x /bin/busybox ]
then
	eselect vi set busybox
fi
$[[steps/chroot/run/extra:lax]]
]

[section portage]

ROOT: /
