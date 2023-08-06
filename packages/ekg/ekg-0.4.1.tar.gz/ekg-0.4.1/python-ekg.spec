# sitelib for noarch packages
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%global pypiname ekg

Name:           python-%{pypiname}
Version:        0.4.1
Release:        1%{?dist}
Summary:        Community Scanning and Reporting Tool

Group:          Applications/Communications
License:        GPLv2+
URL:            http://%{pypiname}.fedorahosted.org/
Source0:        %{pypiname}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

BuildRequires:  python-devel, python-configobj, python-dateutil
BuildRequires:  python-setuptools, python-setuptools-devel, python-sqlalchemy >= 0.5.2
BuildRequires:  python-urlgrabber, python-migrate

%description
EKG is a community health scanner. Currently this targets mailing list
archives, in the future, we may also pay closer attention to code
contributions and other details.

%prep
%setup -q -n %{pypiname}-%{version}


%build

%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%attr(755,root,root) %{_bindir}/ekg-generate-tables
%attr(755,root,root) %{_bindir}/ekg-graph
%attr(755,root,root) %{_bindir}/ekg-scan
%attr(755,root,root) %{_bindir}/ekg-create-db
%attr(755,root,root) %{_bindir}/ekg-migrate
%attr(755,root,root) %{_bindir}/ekg-setup
%attr(755,root,root) %{_bindir}/ekg-upgrade

%doc AUTHORS COPYING README TODO settings.ini
# For noarch packages: sitelib
%{python_sitelib}/*



%changelog
* Fri Jun  5 2009 Yaakov M. Nemoy <ekg@hexago.nl> - 0.4.1-1
- new upstream

* Thu Jun  4 2009 Yaakov M. Nemoy <ekg@hexago.nl> - 0.4.0-2
- fixed up some tabs
- cut description to multiple lines

* Thu Jun  4 2009 Yaakov M. Nemoy <ekg@hexago.nl> - 0.4.0-1
- new upstream

* Sun May 17 2009 Yaakov M. Nemoy <ekg@hexago.nl> - 0.4.0pre1-2
- added new files for new scripts

* Sun May 17 2009 Yaakov M. Nemoy <ekg@hexago.nl> - 0.4.0pre1-1
- new upstream
- adds sqlalchemy-migration support

* Fri May 15 2009 Yaakov M. Nemoy <ekg@hexago.nl> - 0.3.3-2
- adds urlgrabber to Requires because python is a boatload of fail

* Fri May 15 2009 Yaakov M. Nemoy <ekg@hexago.nl> - 0.3.3-1
- new upstream
- new upstream switches to using urlgrabber

* Mon May 11 2009 Yaakov M. Nemoy <ekg@hexago.nl> - 0.3.2-1
- new upstream

* Wed Apr 29 2009 Yaakov M. Nemoy <ekg@hexago.nl> - 0.3.1-1
- new upstream
- updates from distutils to setuputils
- add docs

* Tue Apr 28 2009 Yaakov M. Nemoy <ekg@hexago.nl> - 0.3.0-1
- package creation
- from template with relevant fields filled in
