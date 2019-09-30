# Build -python subpackage
%bcond_without python
# Build -java subpackage
%bcond_without java

%global emacs_version %(pkg-config emacs --modversion)
%global emacs_lispdir %(pkg-config emacs --variable sitepkglispdir)
%global emacs_startdir %(pkg-config emacs --variable sitestartdir)

Summary:        Protocol Buffers - Google's data interchange format
Name:           protobuf
Version:        3.5.0
Release:        8%{?dist}
License:        BSD
URL:            https://github.com/protocolbuffers/protobuf
Source:         https://github.com/protocolbuffers/protobuf/archive/v%{version}.tar.gz
Source1:        ftdetect-proto.vim
Source2:        protobuf-init.el
Source3:        https://github.com/google/googlemock/archive/release-1.7.0.tar.gz#/googlemock-1.7.0.tar.gz
Source4:        https://github.com/google/googletest/archive/release-1.7.0.tar.gz#/googletest-1.7.0.tar.gz


Patch0:         0001-fix-build-on-s390x.patch


BuildRequires:  autoconf automake emacs(bin) emacs-el
BuildRequires:  gcc-c++ libtool pkgconfig zlib-devel
Provides:       %{name}-vim
Provides:       %{name}-emacs
Provides:       %{name}-emacs-el
Obsoletes:      %{name}-vim
Obsoletes:      %{name}-emacs
Obsoletes:      %{name}-emacs-el

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
Obsoletes:      %{name}-compiler
Obsoletes:      %{name}-static

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
Obsoletes:      %{name}-lite-static

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
BuildRequires:  python2-devel python2-setuptools python2-google-apputils
Requires:       python2-six
Conflicts:      %{name}-compiler > %{version}
Conflicts:      %{name}-compiler < %{version}
Provides:       %{name}-python = %{version}-%{release}
%{?python_provide:%python_provide python2-%{name}}

%description -n python2-%{name}
This package contains Python 2 libraries for Google Protocol Buffers

%package -n python%{python3_pkgversion}-%{name}
Summary:        Python 3 bindings for Google Protocol Buffers
BuildArch:      noarch
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-google-apputils
Requires:       python%{python3_pkgversion}-six >= 1.9
Conflicts:      %{name}-compiler > %{version}
Conflicts:      %{name}-compiler < %{version}
Provides:       %{name}-python3 = %{version}-%{release}
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}

%description -n python%{python3_pkgversion}-%{name}
This package contains Python 3 libraries for Google Protocol Buffers
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
Conflicts:      %{name}-compiler > %{version}
Conflicts:      %{name}-compiler < %{version}

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

%package javanano
Summary:        Protocol Buffer JavaNano API
BuildArch:      noarch

%description javanano
JavaNano is a special code generator and runtime
library designed specially for resource-restricted
systems, like Android.

%package parent
Summary:        Protocol Buffer Parent POM
BuildArch:      noarch

%description parent
Protocol Buffer Parent POM.

%endif

%prep
%setup -q -n %{name}-%{version}%{?rcver} -a 3 -a 4
%autopatch -p1

mv googlemock-release-1.7.0 gmock
mv googletest-release-1.7.0 gmock/gtest
find -name \*.cc -o -name \*.h | xargs chmod -x
chmod 644 examples/*

%if %{with java}
%pom_remove_parent java/pom.xml
%pom_remove_dep org.easymock:easymockclassextension java/pom.xml java/*/pom.xml
# These use easymockclassextension
rm java/core/src/test/java/com/google/protobuf/ServiceTest.java

# used by https://github.com/google/libphonenumber
%pom_xpath_inject "pom:project/pom:modules" "<module>../javanano</module>" java
%pom_remove_parent javanano
%pom_remove_dep org.easymock:easymockclassextension javanano

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

make %{?_smp_mflags}

%if %{with python}
pushd python
%py2_build
%py3_build
popd
%endif

%if %{with java}
%mvn_build -s -- -f java/pom.xml
%endif

emacs -batch -f batch-byte-compile editors/protobuf-mode.el

%check
# TODO: failures; get them fixed and remove || :
# https://github.com/protocolbuffers/protobuf/issues/631
make %{?_smp_mflags} check || :

%install
make %{?_smp_mflags} install DESTDIR=%{buildroot} STRIPBINARIES=no INSTALL="%{__install} -p" CPPROG="cp -p"
find %{buildroot} -type f -name "*.la" -exec rm -f {} \;

%if %{with python}
pushd python
#python ./setup.py install --root=%{buildroot} --single-version-externally-managed --record=INSTALLED_FILES --optimize=1
%py2_install
%py3_install
find %{buildroot}%{python2_sitelib} %{buildroot}%{python3_sitelib} -name \*.py |
  xargs sed -i -e '1{\@^#!@d}'
popd
%endif
install -p -m 644 -D %{SOURCE1} %{buildroot}%{_datadir}/vim/vimfiles/ftdetect/proto.vim
install -p -m 644 -D editors/proto.vim %{buildroot}%{_datadir}/vim/vimfiles/syntax/proto.vim

%if %{with java}
%mvn_install
%endif

mkdir -p $RPM_BUILD_ROOT%{emacs_lispdir}
mkdir -p $RPM_BUILD_ROOT%{emacs_startdir}
install -p -m 0644 editors/protobuf-mode.el $RPM_BUILD_ROOT%{emacs_lispdir}
install -p -m 0644 editors/protobuf-mode.elc $RPM_BUILD_ROOT%{emacs_lispdir}
install -p -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{emacs_startdir}

%ldconfig_scriptlets
%ldconfig_scriptlets lite

%files
%{_libdir}/libprotobuf.so.15*
%{_datadir}/vim/vimfiles/ftdetect/proto.vim
%{_datadir}/vim/vimfiles/syntax/proto.vim
%{emacs_startdir}/protobuf-init.el
%{emacs_lispdir}/protobuf-mode.elc
%{emacs_lispdir}/protobuf-mode.el
%doc CHANGES.txt CONTRIBUTORS.txt README.md
%license LICENSE

%files devel
%dir %{_includedir}/google
%{_includedir}/google/protobuf/
%{_bindir}/protoc
%{_libdir}/libprotoc.so.15*
%{_libdir}/libprotobuf.so
%{_libdir}/libprotoc.so
%{_libdir}/pkgconfig/protobuf.pc
%{_libdir}/libprotobuf.a
%{_libdir}/libprotoc.a
%doc README.md examples/add_person.cc examples/addressbook.proto examples/list_people.cc examples/Makefile examples/README.md

%files lite
%{_libdir}/libprotobuf-lite.so.15*

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

%files -n python%{python3_pkgversion}-protobuf
%dir %{python3_sitelib}/google
%{python3_sitelib}/google/protobuf/
%{python3_sitelib}/protobuf-%{version}%{?rcver}-py3.?.egg-info/
%{python3_sitelib}/protobuf-%{version}%{?rcver}-py3.?-nspkg.pth
%doc python/README.md
%doc examples/add_person.py examples/list_people.py examples/addressbook.proto
%endif


%if %{with java}
%files java -f .mfiles-protobuf-java
%doc examples/AddPerson.java examples/ListPeople.java
%doc java/README.md
%license LICENSE

%files java-util -f .mfiles-protobuf-java-util

%files javadoc -f .mfiles-javadoc
%license LICENSE

%files javanano -f .mfiles-protobuf-javanano
%doc javanano/README.md
%license LICENSE

%files parent -f .mfiles-protobuf-parent
%license LICENSE
%endif

%changelog
