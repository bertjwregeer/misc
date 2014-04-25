# Create IPv6 addresses for rc.conf

    for ((I=0, J=2; I <= 32; I++, J++)); do echo -n "ifconfig_em0_alias"$J"="; printf "\"inet6 2607:5300:60:f74::dead:%x prefixlen 128\"\n" $I; done

Cause I am lazy and it is annoying that there is no way to specify a range on
FreeBSD!
