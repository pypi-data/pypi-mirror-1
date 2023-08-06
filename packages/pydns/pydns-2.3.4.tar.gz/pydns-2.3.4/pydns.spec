%define name pydns
%define version 2.3.4
%define release 2.4

Summary: Python DNS library
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
License: Python license
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Anthony Baxter and others <pydns-developer@lists.sourceforge.net>
Packager: Stuart D. Gathman <stuart@bmsi.com>
Url: http://pydns.sourceforge.net/

%description
Python DNS library

%prep
%setup

%build
python2.4 setup.py build

%install
python2.4 setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Tue Jun 09 2009 Stuart Gathman <stuart@bmsi.com> 2.3.4-1
- Support IDNA label encoding
- Optionally support M$ compatible UTF-8 label encoding.
* Fri Aug 01 2008 Stuart Gathman <stuart@bmsi.com> 2.3.3-1
- Support IPv6 nameservers
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
