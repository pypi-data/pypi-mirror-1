%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-director
Version:        1.1.0
Release:        1%{?dist}
Summary:        Command line input plugin system

Group:          Development/Libraries
License:        GPLv3+
URL:            https://fedorahosted.org/director/
Source0:        https://fedorahosted.org/releases/d/i/director/director-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
Requires:       python >= 2.4
BuildRequires:  python-setuptools


%description
A near drop in command line option plugin system for python applications.


%prep
%setup -q -n director-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT/


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc INSTALL LICENSE AUTHORS COPYING
# For noarch packages: sitelib
%{python_sitelib}/*


%changelog
* Wed Oct 11 2008 Steve 'Ashcrow' Milner <smilner+director@redhat.com> - 1.1.0-1
- Updated for upstream 1.1.0

* Fri Aug  1 2008 Steve 'Ashcrow' Milner <smilner+director@redhat.com> - 1.0.2-1
- Updated for upstream 1.0.2

* Fri Jul 18 2008 Steve 'Ashcrow' Milner <smilner+director@redhat.com> - 1.0.1-1
- Issues with some uses of run_code ... fixed.

* Fri Jul 18 2008 Steve 'Ashcrow' Milner <smilner+director@redhat.com> - 1.0.0-1
- Initial spec
