%define webadminroot /var/www/html/admin

#Module-Specific definitions
%define mod_name mod_benchmark
%define mod_conf 93_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Mod_benchmark is a DSO module for the apache Web server
Name:		apache-%{mod_name}
Version:	2.0.0
Release:	%mkrel 6
Group:		System/Servers
License:	GPL
URL:		http://www.trickytools.com/php/mod_benchmark.php
Source0:	%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}.bz2
Patch0:		mod_benchmark-2.0.0-no_cybase.diff
Patch1:		mod_benchmark-1.6-apr.diff
Patch2:		mod_benchmark-2.0.0-apache220.diff
BuildRequires:	autoconf2.5
BuildRequires:	automake1.7
BuildRequires:	mysql-devel
BuildRequires:	postgresql-devel
Requires:	apache-mod_php
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
mod_benchmark is an apache module that produces Performance
Statistics. It can help you find out which are the slower pages,
which are the system bottlenecks. It can also alert you when
thresholds are reached. Reports are displayed through a PHP fronte

NOTE: This software requires the SVG viewer by Adobe to make use
of the graphs produced. (MSIE only?)

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p1
%patch1 -p0
%patch2 -p1


pushd benchmark
# fix dir perms
find . -type d | xargs chmod 755

# fix file perms
find . -type f | xargs chmod 644
popd

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
export WANT_AUTOCONF_2_5=1
rm -f missing
libtoolize --copy --force; aclocal-1.7; autoconf; automake-1.7 --add-missing

export CPPFLAGS="-DLINUX=2 -D_REENTRANT -D_GNU_SOURCE -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE"

%configure2_5x \
    --with-apxs2=%{_sbindir}/apxs \
    --enable-mysql \
    --enable-pgsql \
    --disable-sybase \
    --disable-oracle

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

cp -rp src/.libs .

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
bzcat %{SOURCE1} > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

# install other stuff
install -m755 .libs/benchmark-mysql.so %{buildroot}%{_libdir}/apache-extramodules/
install -m755 .libs/benchmark-pgsql.so %{buildroot}%{_libdir}/apache-extramodules/
install -m755 src/alerter.sh %{buildroot}%{_libdir}/apache-extramodules/
install -m755 src/sysstat2 %{buildroot}%{_libdir}/apache-extramodules/
install -m755 src/benchmark_rt %{buildroot}%{_libdir}/apache-extramodules/

install -d %{buildroot}/%{webadminroot}/%{mod_name}
cp -aRf benchmark/* %{buildroot}/%{webadminroot}/%{mod_name}/

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog INSTALL README TODO plugins
%doc sql/mod_benchmark-mysql.sql sql/mod_benchmark-std.sql sql/mod_benchmark-pgsql.sql
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0644,root,root) %config(noreplace) %{webadminroot}/%{mod_name}/php/globals.inc.php
%attr(0644,root,root) %config(noreplace) %{webadminroot}/%{mod_name}/perl/globals.inc.pl
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%attr(0755,root,root) %{_libdir}/apache-extramodules/alerter.sh
%attr(0755,root,root) %{_libdir}/apache-extramodules/sysstat2
%attr(0755,root,root) %{_libdir}/apache-extramodules/benchmark_rt
%attr(0755,root,root) %{_libdir}/apache-extramodules/benchmark-mysql.so
%attr(0755,root,root) %{_libdir}/apache-extramodules/benchmark-pgsql.so
%{webadminroot}/%{mod_name}/*
