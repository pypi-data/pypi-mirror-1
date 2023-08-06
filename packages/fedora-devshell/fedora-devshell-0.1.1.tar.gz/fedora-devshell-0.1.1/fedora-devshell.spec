# sitelib for noarch packages
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           fedora-devshell
Version:        0.1.1
Release:        1%{?dist}
Summary:        Fedora Developer's Toolbox

Group:          Development/Languages
License:        GPLv2
URL:            https://fedorahosted.org/%{name}/
Source0:        https://fedorahosted.org/releases/f/e/%{name}/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  python-devel, python-setuptools-devel, python-dateutil
BuildRequires:  python-configobj, rpm-python

%description
Fedora Devshell is a developers toolbox for creating packages and developing 
software for Fedora. It aims to simplify the process of creating and 
maintaining packages in the Fedora repositories, and simplify the workflow 
between other Fedora components.

%prep
%setup -q -n %{name}-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{_bindir}/ports
%{_bindir}/devshell
%doc LICENSE TODO PKG-INFO
# For noarch packages: sitelib
%{python_sitelib}/devshell/
%{python_sitelib}/fedora_devshell-*.egg-info


%changelog
* Fri May  1 2009 Yaakov M. Nemoy <devshell@hexago.nl> - 0.1.1-1
- new upstream
- fixes license
- includes upstream URL
- adds PKG-INFO to docs
- more specific file entries for python_sitelib
- upstream removes extraneous shebangs from some scripts

* Thu Apr 30 2009 Yaakov M. Nemoy <devshell@hexago.nl> - 0.1.0-1
- creation

