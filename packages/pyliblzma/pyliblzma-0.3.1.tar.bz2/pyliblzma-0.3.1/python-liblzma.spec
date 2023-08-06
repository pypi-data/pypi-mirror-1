%define	oname	pyliblzma
%define	module	liblzma

Summary:	Python bindings for liblzma
Name:		python-%{module}
Version:	0.3
Release:	%mkrel 1
License:	LGPLv3+
Group:		Development/Python
Url:		http://lzmautils.sourceforge.net/
Source0:	%{oname}-%{version}.tar.lzma
%py_requires -d
BuildRequires:	liblzma-devel python-setuptools
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
PylibLZMA provides a python interface for the liblzma library
to read and write data that has been compressed or can be decompressed
by Lasse Collin's lzma utils.

%prep
%setup -qn %{oname}-%{version}

%build
python setup.py build

%check
python setup.py test

%install
rm -rf %{buildroot}
python setup.py install --root=%{buildroot}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README THANKS
%{python_sitearch}/%{module}.so
%{python_sitearch}/%{oname}*.egg-info

%changelog
* Mon May 19 2008 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.3-1
- initial release
