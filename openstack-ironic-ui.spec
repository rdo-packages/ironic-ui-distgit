%global milestone .0rc1
%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x4c29ff0e437f3351fd82bdf47c5a3bc787dc7035
%global pypi_name ironic-ui
%global mod_name ironic_ui

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global with_doc 1

%global common_desc \
Ironic UI is an OpenStack Horizon plugin that allows users to view and \
manage their bare metal nodes, ports and drivers.

Name:           openstack-%{pypi_name}
Version:        5.0.0
Release:        0.1%{?milestone}%{?dist}
Summary:        OpenStack Ironic Dashboard for Horizon

License:        ASL 2.0
URL:            http://docs.openstack.org/developer/ironic-ui
Source0:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
#
# patches_base=5.0.0.0rc1
#

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif
BuildArch:      noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif
BuildRequires:  python3-devel
BuildRequires:  python3-pbr
BuildRequires:  gettext
BuildRequires:  git-core
BuildRequires:  openstack-macros
# For tests only
BuildRequires:  openstack-dashboard
BuildRequires:  python3-hacking
BuildRequires:  python3-django-horizon
BuildRequires:  python3-ironicclient
BuildRequires:  python3-mock
BuildRequires:  python3-mox3
BuildRequires:  python3-pytest
BuildRequires:  python3-subunit
BuildRequires:  python3-testrepository
BuildRequires:  python3-testscenarios
BuildRequires:  python3-testtools

Requires: openstack-dashboard
Requires: python3-babel
Requires: python3-django
Requires: python3-django-horizon
Requires: python3-ironicclient >= 2.3.0
Requires: python3-pbr

%description
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:    OpenStack Ironic Dashboard for Horizon - documentation
BuildRequires: python3-sphinx
BuildRequires: python3-openstackdocstheme

%description doc
%{common_desc}

This package contains the documentation.
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{pypi_name}-%{upstream_version} -S git
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

%py_req_cleanup

%build
%{py3_build}
# Generate i18n files
pushd build/lib/%{mod_name}
django-admin compilemessages
popd

# generate html docs
export DJANGO_SETTINGS_MODULE=ironic_ui.test.settings

%if 0%{?with_doc}
export PYTHONPATH=$PYTHONPATH:/usr/share/openstack-dashboard/
sphinx-build doc/source html
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}
%endif

%install
%{py3_install}

# Move config to horizon
mkdir -p %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
mv %{mod_name}/enabled/_2200_ironic.py %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py
ln -s ../../../../../..%{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_2200_ironic.py

# Remove .po and .pot (they are not required)
rm -f %{buildroot}%{python3_sitelib}/%{mod_name}/locale/*/LC_*/django*.po
rm -f %{buildroot}%{python3_sitelib}/%{mod_name}/locale/*pot

# Find language files
%find_lang django --all-name


%check
rm -rf ironic_ui/test/integration
PYTHONPATH=/usr/share/openstack-dashboard NOSE_WITH_OPENSTACK=1 %{__python3} manage.py test ironic_ui


%files -f django.lang
%license LICENSE
%{python3_sitelib}/%{mod_name}
%{python3_sitelib}/%{mod_name}-*-py%{python3_version}.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_2200_ironic.py*
%{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py*

%if 0%{?with_doc}
%files doc
%license LICENSE
%doc html README.rst
%endif

%changelog
* Fri Sep 17 2021 RDO <dev@lists.rdoproject.org> 5.0.0-0.1.0rc1
- Update to 5.0.0.0rc1


