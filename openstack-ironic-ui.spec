%global pypi_name ironic-ui
%global mod_name ironic_ui

Name:           openstack-%{pypi_name}
Version:        XXX
Release:        XXX
Summary:        Ironic Dashboard

License:        ASL 2.0
URL:            http://docs.openstack.org/developer/ironic-ui
Source0:        http://tarballs.openstack.org/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-pbr
BuildRequires:  python-sphinx
BuildRequires:  python-oslo-sphinx
# For tests only
BuildRequires:  openstack-dashboard
BuildRequires:  python-hacking
BuildRequires:  python-django-horizon
BuildRequires:  python-django-nose
BuildRequires:  python-django-openstack-auth
BuildRequires:  python-ironicclient
BuildRequires:  python-mock
BuildRequires:  python-mox
BuildRequires:  python-subunit
BuildRequires:  python-testrepository
BuildRequires:  python-testscenarios
BuildRequires:  python-testtools

Requires: python-babel
Requires: python-django
Requires: python-django-compressor
Requires: python-django-horizon
Requires: python-django-openstack-auth
Requires: python-ironicclient
Requires: python-pbr

%description
Ironic Dashboard

%prep
%setup -q -n %{pypi_name}-%{version}
# Remove bundled egg-info
rm -rf %{pypi_name}.egg-info

# generate html docs
sphinx-build doc/source html
# remove the sphinx-build leftovers
rm -rf html/.{doctrees,buildinfo}

rm test-requirements.txt

%build
%{__python2} setup.py build


%install
%{__python2} setup.py install --skip-build --root %{buildroot}

# Move config to horizon
mkdir -p %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled
mkdir -p %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled
mv %{mod_name}/enabled/_2200_ironic.py %{buildroot}%{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py
ln -s %{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py %{buildroot}%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_2200_ironic.py


%check
NOSE_WITH_OPENSTACK=1 %{__python2} manage.py test ironic_ui


%files
%doc html README.rst
%license LICENSE
%{python2_sitelib}/%{mod_name}
%{python2_sitelib}/%{mod_name}-*-py?.?.egg-info
%{_datadir}/openstack-dashboard/openstack_dashboard/local/enabled/_2200_ironic.py*
%{_sysconfdir}/openstack-dashboard/enabled/_2200_ironic.py*


%changelog

