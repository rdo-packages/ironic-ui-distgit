# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%global pypi_name ironic-ui
%global mod_name ironic_ui

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global with_doc 1

%global common_desc \
Ironic UI is an OpenStack Horizon plugin that allows users to view and \
manage their bare metal nodes, ports and drivers.

Name:           openstack-%{pypi_name}
Version:        3.5.3
Release:        1%{?dist}
Summary:        OpenStack Ironic Dashboard for Horizon

License:        ASL 2.0
URL:            http://docs.openstack.org/developer/ironic-ui
Source0:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
BuildArch:      noarch
BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-pbr
BuildRequires:  gettext
BuildRequires:  git
BuildRequires:  openstack-macros
# For tests only
BuildRequires:  openstack-dashboard
BuildRequires:  python%{pyver}-hacking
BuildRequires:  python%{pyver}-django-horizon
BuildRequires:  python%{pyver}-ironicclient
BuildRequires:  python%{pyver}-mock
BuildRequires:  python%{pyver}-mox3
BuildRequires:  python%{pyver}-subunit
BuildRequires:  python%{pyver}-testrepository
BuildRequires:  python%{pyver}-testscenarios
BuildRequires:  python%{pyver}-testtools

Requires: openstack-dashboard
Requires: python%{pyver}-babel
Requires: python%{pyver}-django
Requires: python%{pyver}-django-horizon
Requires: python%{pyver}-ironicclient >= 2.3.0
Requires: python%{pyver}-pbr

%description
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:    OpenStack Ironic Dashboard for Horizon - documentation
BuildRequires: python%{pyver}-sphinx
BuildRequires: python%{pyver}-openstackdocstheme

%description doc
%{common_desc}

This package contains the documentation.
%endif

%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%py_req_cleanup

%build
%{pyver_build}
# Generate i18n files
pushd build/lib/%{mod_name}
django-admin compilemessages
popd

# generate html docs
export DJANGO_SETTINGS_MODULE=ironic_ui.test.settings

%if 0%{?with_doc}
export PYTHONPATH=$PYTHONPATH:/usr/share/openstack-dashboard/
sphinx-build-%{pyver} doc/source html
# remove the sphinx-build-%{pyver} leftovers
rm -rf html/.{doctrees,buildinfo}
%endif

%install
%{pyver_install}

# Move config to horizon
mkdir -p %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
mv %{mod_name}/enabled/_2200_ironic.py %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py
ln -s %{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_2200_ironic.py

# Remove .po and .pot (they are not required)
rm -f %{buildroot}%{pyver_sitelib}/%{mod_name}/locale/*/LC_*/django*.po
rm -f %{buildroot}%{pyver_sitelib}/%{mod_name}/locale/*pot

# Find language files
%find_lang django --all-name


%check
rm -rf ironic_ui/test/integration
PYTHONPATH=/usr/share/openstack-dashboard NOSE_WITH_OPENSTACK=1 %{pyver_bin} manage.py test ironic_ui


%files -f django.lang
%license LICENSE
%{pyver_sitelib}/%{mod_name}
%{pyver_sitelib}/%{mod_name}-*-py?.?.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_2200_ironic.py*
%{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py*

%if 0%{?with_doc}
%files doc
%license LICENSE
%doc html README.rst
%endif

%changelog
* Fri Oct 11 2019 RDO <dev@lists.rdoproject.org> 3.5.3-1
- Update to 3.5.3

* Mon Sep 30 2019 RDO <dev@lists.rdoproject.org> 3.5.2-1
- Update to 3.5.2


