# Copyright 2008 University of Bern
# Distributed under the terms of the GNU General Public License v3
# $Header: $

NEED_PYTHON=2.5

inherit distutils

DESCRIPTION="ldaptool is a toolkit for manipulating LDAP databases"
HOMEPAGE="http://www.ox9.org/projects/ldaptool/"
SRC_URI="http://cheeseshop.python.org/packages/source/l/${PN}/${P}.tar.gz"

LICENSE="GPL-3"
SLOT="0"
KEYWORDS="~amd64 ~ia64 ~x86 ~ppc64 ~sparc ~x86-macos ~ppc-macos"
IUSE=""

DEPEND=">=dev-python/setuptools-0.6_rc8
	dev-python/python-ldap
	doc ? ( >=dev-python/sphinx-0.5 )"
RDEPEND="${DEPEND}"

src_compile() {
	distutils_src_compile

	if use doc; then
		cd doc
		emake html || die "failed to build documentation"
	fi
}

src_install() {
	distutils_src_install
	if use doc; then
		dohtml -A txt -r doc/build/html*
	fi
	doman doc/ldaptool.8
}

src_test() {
	# Hmm.. does distutils eclass really not provide a test construct?
	${python} setup.py test || die "Tests failed"
}

