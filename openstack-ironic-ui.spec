%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
%global pypi_name ironic-ui
%global mod_name ironic_ui

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order nodeenv xvfbwrapper
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif
%global with_doc 1

%global common_desc \
Ironic UI is an OpenStack Horizon plugin that allows users to view and \
manage their bare metal nodes, ports and drivers.

Name:           openstack-%{pypi_name}
Version:        XXX
Release:        XXX
Summary:        OpenStack Ironic Dashboard for Horizon

License:        Apache-2.0
URL:            http://docs.openstack.org/developer/ironic-ui
Source0:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
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
BuildRequires:  pyproject-rpm-macros
BuildRequires:  gettext
BuildRequires:  git-core
BuildRequires:  openstack-macros
BuildRequires:  openstack-dashboard
Requires: openstack-dashboard
%description
%{common_desc}

%if 0%{?with_doc}
%package doc
Summary:    OpenStack Ironic Dashboard for Horizon - documentation
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


sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini
# Disable warnint-is-error in doc build
sed -i '/sphinx-build/ s/-W//' tox.ini

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
export PYTHONPATH=.:%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}:/usr/share/openstack-dashboard/
%pyproject_wheel

# generate html docs
export DJANGO_SETTINGS_MODULE=ironic_ui.test.settings

%if 0%{?with_doc}
%tox -e docs
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}
%endif

%install
%pyproject_install

# Generate i18n files
pushd %{buildroot}/%{python3_sitelib}/%{mod_name}
django-admin compilemessages
popd

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
export PYTHONPATH=.:%{buildroot}%{python3_sitearch}:%{buildroot}%{python3_sitelib}:/usr/share/openstack-dashboard/
%tox -e %{default_toxenv}

%files -f django.lang
%license LICENSE
%{python3_sitelib}/%{mod_name}
%{python3_sitelib}/%{mod_name}-*.dist-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_2200_ironic.py*
%{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py*

%if 0%{?with_doc}
%files doc
%license LICENSE
%doc doc/build/html README.rst
%endif

%changelog

