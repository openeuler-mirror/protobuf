# Build -python subpackage
%bcond_without python
# Build -java subpackage
%bcond_with java
%bcond_without python3

#global rcver rc2

Summary:        Protocol Buffers - Google's data interchange format
Name:           protobuf
Version:        3.12.3
Release:        10
License:        BSD
URL:            https://github.com/protocolbuffers/protobuf
Source:         https://github.com/protocolbuffers/protobuf/releases/download/v%{version}%{?rcver}/%{name}-all-%{version}%{?rcver}.tar.gz
Source1:        protobuf-init.el

Patch9000:      0001-add-secure-compile-option-in-Makefile.patch

BuildRequires:  autoconf automake emacs gcc-c++ libtool pkgconfig zlib-devel
Requires:       emacs-filesystem >= %{_emacs_version} vim-enhanced
Provides:       %{name}-vim
Provides:       %{name}-emacs
Provides:       %{name}-emacs-el
Obsoletes:      %{name}-vim < 3.12.3
Obsoletes:      %{name}-emacs < 3.12.3
Obsoletes:      %{name}-emacs-el < 3.12.3

%description

Protocol Buffers (a.k.a., protobuf) are Google's language-neutral,
platform-neutral, extensible mechanism for serializing structured data.
You can find protobuf's documentation on the Google Developers site.

%package devel
Summary:        Protocol Buffers C++ headers and libraries
Requires:       %{name} = %{version}-%{release}
Requires:       zlib-devel pkgconfig
Provides:       %{name}-compiler
Provides:       %{name}-static
Obsoletes:      %{name}-compiler < 3.12.3
Obsoletes:      %{name}-static < 3.12.3

%description devel
This package contains Protocol Buffers compiler for all languages and
C++ headers and libraries

%package lite
Summary:        Protocol Buffers LITE_RUNTIME libraries

%description lite
Protocol Buffers built with optimize_for = LITE_RUNTIME.

The "optimize_for = LITE_RUNTIME" option causes the compiler to generate code
which only depends libprotobuf-lite, which is much smaller than libprotobuf but
lacks descriptors, reflection, and some other features.

%package lite-devel
Summary:        Protocol Buffers LITE_RUNTIME development libraries
Requires:       %{name}-devel = %{version}-%{release}
Requires:       %{name}-lite = %{version}-%{release}
Provides:       %{name}-lite-static
Obsoletes:      %{name}-lite-static < 3.12.3

%description lite-devel
This package contains development libraries built with
optimize_for = LITE_RUNTIME.

The "optimize_for = LITE_RUNTIME" option causes the compiler to generate code
which only depends libprotobuf-lite, which is much smaller than libprotobuf but
lacks descriptors, reflection, and some other features.

%if %{with python}
%package -n python2-%{name}
Summary:        Python 2 bindings for Google Protocol Buffers
BuildArch:      noarch
BuildRequires:  python2-devel python2-setuptools
BuildRequires:  python2-google-apputils
Requires:       python2-six
Obsoletes:      %{name}-python < 3.1.0-4
Provides:       %{name}-python = %{version}-%{release}
%{?python_provide:%python_provide python2-%{name}}

%description -n python2-%{name}
This package contains Python 2 libraries for Google Protocol Buffers

%if %{with python3}
%package -n python%{python3_pkgversion}-%{name}
Summary:        Python 3 bindings for Google Protocol Buffers
BuildArch:      noarch
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
# For tests
BuildRequires:  python%{python3_pkgversion}-google-apputils
Requires:       python%{python3_pkgversion}-six >= 1.9
Provides:       %{name}-python3 = %{version}-%{release}
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}

%description -n python%{python3_pkgversion}-%{name}
This package contains Python 3 libraries for Google Protocol Buffers
%endif
%endif


%if %{with java}
%package java
Summary:        Java Protocol Buffers runtime library
BuildArch:      noarch
BuildRequires:  maven-local
BuildRequires:  mvn(com.google.code.gson:gson)
BuildRequires:  mvn(com.google.guava:guava)
BuildRequires:  mvn(junit:junit)
BuildRequires:  mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-antrun-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-source-plugin)
BuildRequires:  mvn(org.codehaus.mojo:build-helper-maven-plugin)
BuildRequires:  mvn(org.easymock:easymock)
Obsoletes:      %{name}-javanano < 3.6.0

%description java
This package contains Java Protocol Buffers runtime library.

%package java-util
Summary:        Utilities for Protocol Buffers
BuildArch:      noarch

%description java-util
Utilities to work with protos. It contains JSON support
as well as utilities to work with proto3 well-known types.

%package javadoc
Summary:        Javadoc for %{name}-java
BuildArch:      noarch

%description javadoc
This package contains the API documentation for %{name}-java.

%package parent
Summary:        Protocol Buffer Parent POM
BuildArch:      noarch

%description parent
Protocol Buffer Parent POM.

%endif

%prep
%setup -q -n %{name}-%{version}%{?rcver}
%autopatch -p1
find -name \*.cc -o -name \*.h | xargs chmod -x
chmod 644 examples/*
%if %{with java}
%pom_remove_parent java/pom.xml
%pom_remove_dep org.easymock:easymockclassextension java/pom.xml java/*/pom.xml
# These use easymockclassextension
rm java/core/src/test/java/com/google/protobuf/ServiceTest.java
#rm -r java/core/src/test

# Make OSGi dependency on sun.misc package optional
%pom_xpath_inject "pom:configuration/pom:instructions" "<Import-Package>sun.misc;resolution:=optional,*</Import-Package>" java/core

# Backward compatibility symlink
%mvn_file :protobuf-java:jar: %{name}/%{name}-java %{name}

# This test is incredibly slow on arm
# https://github.com/protocolbuffers/protobuf/issues/2389
%ifarch %{arm}
mv java/core/src/test/java/com/google/protobuf/IsValidUtf8Test.java \
   java/core/src/test/java/com/google/protobuf/IsValidUtf8Test.java.slow
%endif
%endif

rm -f src/solaris/libstdc++.la

%build
iconv -f iso8859-1 -t utf-8 CONTRIBUTORS.txt > CONTRIBUTORS.txt.utf8
mv CONTRIBUTORS.txt.utf8 CONTRIBUTORS.txt
export PTHREAD_LIBS="-lpthread"
./autogen.sh
%configure

%make_build

%if %{with python}
pushd python
%py2_build
%if %{with python3}
%py3_build
%endif
popd
%endif

%if %{with java}
%mvn_build -s -- -f java/pom.xml
%endif

%{_emacs_bytecompile} editors/protobuf-mode.el


%check
# Java tests fail on s390x
%ifarch s390x
fail=0
%else
fail=1
%endif
make %{?_smp_mflags} check || exit $fail


%install
%make_install %{?_smp_mflags} STRIPBINARIES=no INSTALL="%{__install} -p" CPPROG="cp -p"
find %{buildroot} -type f -name "*.la" -exec rm -f {} \;

%if %{with python}
pushd python
#python ./setup.py install --root=%{buildroot} --single-version-externally-managed --record=INSTALLED_FILES --optimize=1
%py2_install
%if %{with python3}
%py3_install
%endif
find %{buildroot}%{python2_sitelib} %{buildroot}%{python3_sitelib} -name \*.py |
  xargs sed -i -e '1{\@^#!@d}'
popd
%endif

%if %{with java}
%mvn_install
%endif

mkdir -p %{buildroot}%{_emacs_sitelispdir}/%{name}
install -p -m 0644 editors/protobuf-mode.el %{buildroot}%{_emacs_sitelispdir}/%{name}
install -p -m 0644 editors/protobuf-mode.elc %{buildroot}%{_emacs_sitelispdir}/%{name}
mkdir -p %{buildroot}%{_emacs_sitestartdir}
install -p -m 0644 %{SOURCE1} %{buildroot}%{_emacs_sitestartdir}

%ldconfig_scriptlets
%ldconfig_scriptlets lite
%ldconfig_scriptlets compiler

%files
%doc CHANGES.txt CONTRIBUTORS.txt README.md
%license LICENSE
%{_libdir}/libprotobuf.so.23*
%doc README.md
%license LICENSE
%{_bindir}/protoc
%{_libdir}/libprotoc.so.23*
%{_emacs_sitelispdir}/%{name}/
%{_emacs_sitestartdir}/protobuf-init.el

%files devel
%dir %{_includedir}/google
%{_includedir}/google/protobuf/
%{_libdir}/libprotobuf.so
%{_libdir}/libprotoc.so
%{_libdir}/pkgconfig/protobuf.pc
%doc examples/add_person.cc examples/addressbook.proto examples/list_people.cc examples/Makefile examples/README.md
%{_libdir}/libprotobuf.a
%{_libdir}/libprotoc.a

%files lite
%{_libdir}/libprotobuf-lite.so.23*

%files lite-devel
%{_libdir}/libprotobuf-lite.so
%{_libdir}/pkgconfig/protobuf-lite.pc
%{_libdir}/libprotobuf-lite.a

%if %{with python}
%files -n python2-protobuf
%dir %{python2_sitelib}/google
%{python2_sitelib}/google/protobuf/
%{python2_sitelib}/protobuf-%{version}%{?rcver}-py2.?.egg-info/
%{python2_sitelib}/protobuf-%{version}%{?rcver}-py2.?-nspkg.pth
%doc python/README.md
%doc examples/add_person.py examples/list_people.py examples/addressbook.proto

%if %{with python3}
%files -n python%{python3_pkgversion}-protobuf
%dir %{python3_sitelib}/google
%{python3_sitelib}/google/protobuf/
%{python3_sitelib}/protobuf-%{version}%{?rcver}-py3.?.egg-info/
%{python3_sitelib}/protobuf-%{version}%{?rcver}-py3.?-nspkg.pth
%doc python/README.md
%doc examples/add_person.py examples/list_people.py examples/addressbook.proto
%endif
%endif

%if %{with java}
%files java -f .mfiles-protobuf-java
%doc examples/AddPerson.java examples/ListPeople.java
%doc java/README.md
%license LICENSE

%files java-util -f .mfiles-protobuf-java-util

%files javadoc -f .mfiles-javadoc
%license LICENSE

%files parent -f .mfiles-protobuf-parent
%license LICENSE
%endif

%changelog
* Thu Jul 16 2020 openEuler Buildteam <buildteam@openeuler.org> - 3.12.3-10
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:upgrade from 3.9.0 to 3.12.3

* Wed Apr 08 2020 openEuler Buildteam <buildteam@openeuler.org> - 3.9.0-9
- Type:enhancement
- ID:NA
- SUG:NA
- DESC: remove unnecessary files

* Thu Dec 12 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.9.0-8.h3
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:add bind now secure compile option

* Wed Nov 27 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.9.0-8.h2
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:compatible to centos 7.5

* Tue Nov 26 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.9.0-8.h1
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:upgrade from 3.5.0 to 3.9.0

* Fri Nov 01 2019 openEuler Buildteam <buildteam@openeuler.org> - 3.5.0-8.h1
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:change patch's names according to new rules
