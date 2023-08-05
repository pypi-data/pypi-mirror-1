# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /cvsroot/pyenchant/pyenchant/tools/pyenchant-1.2.0.ebuild,v 1.1 2006/10/08 08:05:14 rynklly Exp $

inherit distutils

DESCRIPTION="Python wrapper for the Enchant spellchecking wrapper library"
SRC_URI="mirror://sourceforge/pyenchant/${P}.tar.gz"
HOMEPAGE="http://pyenchant.sourceforge.net"

IUSE=""
SLOT="0"
KEYWORDS="~x86 ~amd64"
LICENSE="LGPL-2.1"

DEPEND=">=dev-lang/python-2.3
        >=app-text/enchant-1.3.0"


