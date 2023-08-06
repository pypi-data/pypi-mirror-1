#!/bin/bash
# Copyright (c) 2008 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# fail on first error and on unset variables
set -u -e

NAME=${NAME:-101}
MEM=${MEM:-512000}
GUESTHOSTNAME=${GUESTHOSTNAME:-testopenvz}
GUESTDOMAINNAME=${GUESTDOMAIN:-logilab.com}
TEMPLATE=${TEMPLATE:-debian-4.0-x86}
NET1_MAC_INT=${NET_MAC_INT:-24:42:53:21:52:45}
NET1_MAC_EXT=${NET_MAC_EXT:-24:42:53:21:52:46}
NET1_IP=${NET01_IP:-172.17.4.5}
NET1_CIDR=${NET_CIDR:-24}
GATEWAY=${GATEWAY:-213.215.7.51 213.215.7.51}
NAMESERVER1=${NAMESERVER1:-213.215.7.51}
NAMESERVER2=${NAMESERVER2:-213.215.7.52}
NET2_MAC_INT=${NET_MAC_INT:-24:42:53:21:52:47}
NET2_MAC_EXT=${NET_MAC_EXT:-24:42:53:21:52:48}
NET2_IP=${NET01_IP:-172.17.4.6}
NET2_CIDR=${NET_MASK:-24}

logilabvm --create --verbose \
    --type openvz \
    --sys name=$NAME,mem=$MEM,host=$GUESTHOSTNAME,domain=$GUESTDOMAINNAME,ostemplate=$TEMPLATE,ns=$NAMESERVER1,ns=$NAMESERVER2,gw=$GATEWAY \
    --dev template=$TEMPLATE \
    --net method=user,mac=$NET1_MAC_EXT,mac_int=$NET1_MAC_INT,ip=$NET1_IP,cidr=$NET1_CIDR \
    --net method=user,mac=$NET2_MAC_EXT,mac_int=$NET2_MAC_INT,ip=$NET2_IP,cidr=$NET2_CIDR
