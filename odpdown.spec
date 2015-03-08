#
# spec file for package python-odpdown
#
# Copyright (c) 2015 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


Name:           python-odpdown
Version:        0
Release:        0
Summary:        Generate OpenDocument Presentation (odp) files from markdown
License:        BSD-3-Clause
Group:          Development/Languages/Python
Url:            https://github.com/thorstenb/odpdown.git
Source:         https://pypi.python.org/packages/source/o/odpdown/odpdown-%{version}.tar.gz
BuildRequires:  python-devel
BuildRequires:  python-lpod >= 1.1.6
BuildRequires:  python-mistune >= 0.5
BuildRequires:  python-setuptools
Requires:       python-lpod >= 1.1.6
Requires:       python-mistune >= 0.5
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch
%if 0%{?fedora} || 0%{?centos} || 0%{?rhel}
BuildRequires:  python-pygments >= 1.6
Requires:       python-pygments >= 1.6
%else
BuildRequires:  python-Pygments >= 1.6
Requires:       python-Pygments >= 1.6
%endif
%if 0%{?suse_version}
# optional runtime dependencies
Recommends:     python-Pillow >= 2.0
Recommends:     python-beautifulsoup
%else
Requires:       python-Pillow >= 2.0
Requires:       python-BeautifulSoup
%endif

%description
Generate ODP files from markdown.

Have a tool like pandoc, latex beamer etc, that you can write (or
auto-generate) input for within your favourite hacker's editor, and
generate nice-looking slides from. Using your corporation's mandatory,
CI-compliant and lovely-artsy Impress template. Including
syntax-highlighted code snippets of your latest hack, auto-fitted into
the slides.

Usage: odpdown -h will tell you.

%prep
%setup -q -n odpdown-%{version}

%build
python setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=%{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE CHANGES README.md TODO.md
%{_bindir}/odpdown
%{python_sitelib}/*

%changelog
