# rpmbuild parameters:
# --without check: Do not run the testsuite.  Default is to run it.

Summary: An unwinding library
Name: libunwind
Epoch: 2
Version: 1.2
Release: 2%{?dist}
License: BSD
Group: Development/Debuggers
Source: http://download.savannah.gnu.org/releases/libunwind/libunwind-%{version}.tar.gz

Patch2: 0002-Fix-rpmdiff-failure.patch

URL: http://savannah.nongnu.org/projects/libunwind
ExclusiveArch: %{arm} aarch64 %{ix86} x86_64 %{power64}

BuildRequires: automake libtool autoconf

# host != target would cause REMOTE_ONLY build even if building i386 on x86_64.
%global _host %{_target_platform}

%description
Libunwind provides a C ABI to determine the call-chain of a program.

%package devel
Summary: Development package for libunwind
Group: Development/Debuggers
Requires: libunwind = %{epoch}:%{version}-%{release}

%description devel
The libunwind-devel package includes the libraries and header files for
libunwind.

%prep
%setup -q

%patch2 -p1

%build
aclocal
libtoolize --force
autoheader
automake --add-missing
autoconf
%configure --enable-static --enable-shared --disable-setjmp
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'

# /usr/include/libunwind-ptrace.h
# [...] aren't really part of the libunwind API.  They are implemented in
# a archive library called libunwind-ptrace.a.
mv -f $RPM_BUILD_ROOT%{_libdir}/libunwind-ptrace.a $RPM_BUILD_ROOT%{_libdir}/libunwind-ptrace.a-save
rm -f $RPM_BUILD_ROOT%{_libdir}/libunwind*.a
mv -f $RPM_BUILD_ROOT%{_libdir}/libunwind-ptrace.a-save $RPM_BUILD_ROOT%{_libdir}/libunwind-ptrace.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libunwind-ptrace*.so*

#Copy doc files manually as we do not have latex2man in Red Hat Enterprise Linux
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man3
cd doc
for fn in *.man; do
  install -c -m 644 $fn $RPM_BUILD_ROOT%{_mandir}/man3/${fn%.man}.3
done
cd ..

%check
%if 0%{?_with_check:1} || 0%{?_with_testsuite:1}
echo ====================TESTING=========================
make check || true
echo ====================TESTING END=====================
%else
echo ====================TESTSUITE DISABLED=========================
%endif

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc COPYING README NEWS
%{_libdir}/libunwind*.so.*

%files devel
%defattr(-,root,root,-)
%{_libdir}/libunwind*.so
%{_libdir}/libunwind-ptrace.a
%{_libdir}/pkgconfig/libunwind*.pc
%{_mandir}/man3/*
# <unwind.h> does not get installed for REMOTE_ONLY targets - check it.
%{_includedir}/unwind.h
%{_includedir}/libunwind*.h

%changelog
* Mon Feb 27 2017 Miroslav Rezanina <mrezanin@redhat.com> 1.2-2.el7
- Rebase to 1.2 [bz#1384435]
- Resolves: bz#1384435
  (Rebase libunwind package (and add for ppc64le): libunwind)

* Thu Jan 28 2016 Miroslav Rezanina <mrezanin@redhat.com> 1.1-6.el7
- Fix update from EPEL version [bz#1289950]
- Resolves: bz#1289950
  (libunwind in RHEL 7.2 has a smaller release than the last libunwind package in EPEL-7)

* Wed Jul 29 2015 Miroslav Rezanina <mrezanin@redhat.com> 1.1-5
- Version bumped [bz#1238864]
- Resolves: bz#1238864
  libunwind: bump version to win against existing branches

* Fri Jun 19 2015 Miroslav Rezanina <mrezanin@redhat.com> 1.1-2
- lu-Fix-rpmdiff-failure.patch [bz#1229359]
- lu-Fix-buffer-overflow-reported-by-Coverity.patch [bz#1233114]
- Resolves: bz#1229359
  (Fix multilib support)
- Resolves: bz#1233114
  (fix off-by-one in dwarf_to_unw_regnum (CVE-2015-3239))

* Tue Jun 02 2015 Miroslav Rezanina <mrezanin@redhat.com> 1.1-1
- Import to RHEL
