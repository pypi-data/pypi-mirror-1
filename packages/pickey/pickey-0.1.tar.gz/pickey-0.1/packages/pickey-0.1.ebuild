# Copyright 1999-2008 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo-x86/dev-python/paste/paste-1.6.ebuild,v 1.2 2008/05/13 13:21:08 hawking Exp $

NEED_PYTHON=2.4

inherit distutils

KEYWORDS="~amd64 ~x86"

MY_PN=pickey
MY_P=${MY_PN}-${PV}

DESCRIPTION="The WSGI middleware to generate authentication picture key."
HOMEPAGE=""
SRC_URI="http://what/${MY_P}.tar.gz"
LICENSE="MIT"
SLOT="0"
IUSE="doc"

RDEPEND=">=dev-python/paste-1.7
	>=dev-python/beaker-0.9.4"
DEPEND="${RDEPEND}
	dev-python/setuptools
	doc? ( dev-python/pudge dev-python/buildutils )"

S=${WORKDIR}/${MY_P}

src_unpack() {
	distutils_src_unpack

	sed -i \
		-e '/highlighter/d' \
		setup.cfg || die "sed failed"
}

src_compile() {
	distutils_src_compile
	if use doc ; then
		einfo "Generating docs as requested..."
		PYTHONPATH=. "${python}" setup.py pudge || die "generating docs failed"
	fi
}

src_install() {
	distutils_src_install
	use doc && dohtml -r docs/html/*
}

# src_test() needs py.test but there's no release yet
