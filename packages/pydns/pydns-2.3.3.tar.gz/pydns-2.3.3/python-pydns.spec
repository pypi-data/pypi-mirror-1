%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-pydns
Version:        2.3.3
Release:        2%{?dist}
Summary:        Python module for DNS (Domain Name Service).

Group:          Development/Languages
License:        Python Software Foundation License
URL:            http://pydns.sourceforge.net/
Source0:        pydns-%{version}.tar.gz
Patch0:         pydns-%{version}.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
#BuildRequires:  python-setuptools

%description
This is a another release of the pydns code, as originally written by
Guido van Rossum, and with a hopefully nicer API bolted over the
top of it by Anthony Baxter <anthony@interlink.com.au>.

This package contains a module (dnslib) that implements a DNS
(Domain Name Server) client, plus additional modules that define some
symbolic constants used by DNS (dnstype, dnsclass, dnsopcode).

%define namewithoutpythonprefix %(echo %{name} | sed 's/^python-//')
%prep
%setup -q -n %{namewithoutpythonprefix}-%{version}
%patch -b .bms

%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc CREDITS.txt PKG-INFO README-guido.txt README.txt
%{python_sitelib}/DNS/*.py*

%changelog
* Thu Jul 24 2008 Stuart Gathman <stuart@bmsi.com> 2.3.2-2
- Fix tcp timeout
* Thu Jul 24 2008 Stuart Gathman <stuart@bmsi.com> 2.3.2-1
- Randomize TID and source port
* Tue May 22 2007 Stuart Gathman <stuart@bmsi.com> 2.3.1-1
- Bug fix release
- BTS Patches:
- 01resolv-conf-parse patch, thanks to Arnaud Fontaine <arnaud@andesi.org>
  (closes: #378991)
- Changes from Ubuntu (SF = Sourceforge project bug #) (closes: #411138):
- 02utf-8 patch for files with UTF-8 content
- 03socket-error-trap patch, Added DNSError trap for socket.error.
- 04lazy-init SF 1563723 lazy should initilize defaults['server']
- 05addr2bin2addr SF 863364 Mac OS X, Win2000 DHCP, addr2bin and bin2addr.
- 06win32-fix SF 1180344 win32dns.py fails on windows server 2003
- 07unpacker SF 954095 Bug in DNS.Lib.Unpacker.getbyte()
- 08import-lib SF 658601 Missing "import Lib"; for TCP protocol
* Tue Aug 29 2006 Sean Reifschneider <jafo@tummy.com> 2.3.0-1
- Initial RPM spec file.
