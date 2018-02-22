%global pypi_name ironic-ui
%global mod_name ironic_ui

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

%global common_desc \
Ironic UI is an OpenStack Horizon plugin that allows users to view and \
manage their bare metal nodes, ports and drivers.

Name:           openstack-%{pypi_name}
Version:        3.1.1
Release:        1%{?dist}
Summary:        OpenStack Ironic Dashboard for Horizon

License:        ASL 2.0
URL:            http://docs.openstack.org/developer/ironic-ui
Source0:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python2-pbr
BuildRequires:  gettext
BuildRequires:  git
# For tests only
BuildRequires:  openstack-dashboard
BuildRequires:  python2-hacking
BuildRequires:  python-django-horizon
BuildRequires:  python2-django-nose
BuildRequires:  python2-ironicclient
BuildRequires:  python2-mox3
BuildRequires:  python2-subunit
BuildRequires:  python2-testrepository
BuildRequires:  python2-testscenarios
BuildRequires:  python2-testtools

Requires: openstack-dashboard
Requires: python2-babel
Requires: python2-django
Requires: python-django-horizon
Requires: python2-ironicclient >= 2.2.0
Requires: python2-pbr

%description
%{common_desc}

%package doc
Summary:    OpenStack Ironic Dashboard for Horizon - documentation
BuildRequires: python2-sphinx
BuildRequires: python2-openstackdocstheme
BuildRequires: openstack-macros

%description doc
%{common_desc}

This package contains the documentation.

%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%py_req_cleanup

%build
%{__python2} setup.py build
# Generate i18n files
pushd build/lib/%{mod_name}
django-admin compilemessages
popd

# generate html docs
export DJANGO_SETTINGS_MODULE=ironic_ui.test.settings
export PYTHONPATH=$PYTHONPATH:/usr/share/openstack-dashboard/
sphinx-build doc/source html
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}


%install
%{__python2} setup.py install --skip-build --root %{buildroot}

# Move config to horizon
mkdir -p %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
mv %{mod_name}/enabled/_2200_ironic.py %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py
ln -s %{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_2200_ironic.py

# Remove .po and .pot (they are not required)
rm -f %{buildroot}%{python2_sitelib}/%{mod_name}/locale/*/LC_*/django*.po
rm -f %{buildroot}%{python2_sitelib}/%{mod_name}/locale/*pot

# Find language files
%find_lang django --all-name


%check
PYTHONPATH=/usr/share/openstack-dashboard NOSE_WITH_OPENSTACK=1 %{__python2} manage.py test ironic_ui


%files -f django.lang
%license LICENSE
%{python2_sitelib}/%{mod_name}
%{python2_sitelib}/%{mod_name}-*-py?.?.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_2200_ironic.py*
%{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py*

%files doc
%license LICENSE
%doc html README.rst


%changelog
* Thu Feb 22 2018 RDO <dev@lists.rdoproject.org> 3.1.1-1
- Update to 3.1.1

* Sat Feb 17 2018 RDO <dev@lists.rdoproject.org> 3.1.0-1
- Update to 3.1.0


