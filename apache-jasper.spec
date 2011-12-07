# Copyright (c) 2000-2009, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define packdname apache-tomcat-%{version}-src

# This spec file was created by modifying the tomcat5 spec file.  All patches
# applied to the jasper source or catalina (indirectly referenced in the jasper
# build properties) are retained.

Name: apache-jasper
Version: 5.5.28
Release: 3%{dist}
Summary: Jasper OSGi Bundle
Group: Development
License: ASL 2.0
URL: http://tomcat.apache.org
Source0: http://www.apache.org/dist/tomcat/tomcat-5/v%{version}/src/%{packdname}.tar.gz
Source7: jasper-OSGi-MANIFEST.MF
Patch4: %{name}-5.5-jtj-build.patch
Patch7: %{name}-5.5-catalina.sh.patch
Patch8: %{name}-5.5-jasper.sh.patch
Patch9: %{name}-5.5-jspc.sh.patch
Patch10: %{name}-5.5-setclasspath.sh.patch
Patch15: %{name}-5.5-unversioned-commons-logging-jar.patch
Patch16: %{name}-5.5-jspc-classpath.patch

BuildRoot: %{_tmppath}/%{name}-%{epoch}-%{version}-%{release}-root
BuildArch: noarch

Buildrequires: jpackage-utils >= 0:1.7.4
BuildRequires: java-1.6.0-devel
BuildRequires: ant >= 0:1.6.5
BuildRequires: ecj >= 0:3.3.1.1
BuildRequires: jakarta-commons-logging >= 0:1.0.4
BuildRequires: jakarta-commons-el >= 0:1.0
BuildRequires: zip
BuildRequires: apache-tomcat-apis
Requires: jakarta-commons-logging >= 0:1.0.4
Requires: jakarta-commons-el >= 0:1.0
Requires: ecj >= 0:3.3.1.1
Requires: jpackage-utils >= 0:1.7.4
Requires: java-1.6.0-devel
Requires: apache-tomcat-apis

%description
Eclipse plugin for Jasper support.

%package javadoc
Group: Documentation
Summary: Javadoc for Jasper

%description javadoc
API documentation for Jasper.

%prep
%{__rm} -rf ${RPM_BUILD_DIR}/%{name}-%{version}

%setup -q -c -T -a 0
cd %{packdname}
%patch4 -p0
%patch7 -p0
%patch8 -p0
%patch9 -p0
%patch10 -p0
%patch15 -p0
%patch16 -p0
%{__sed} -i -e 's|\@JAVA_HOME\@|%{java_home}|' build/build.xml

%build
# remove pre-built binaries
for dir in ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname} ; do
    find $dir \( -name "*.jar" -o -name "*.class" \) | xargs -t %{__rm} -f
done
# copy license for later doc files declaration
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}
    %{__cp} -p build/LICENSE .
popd 
# build jasper subpackage
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/jasper
    %{__cat} > build.properties << EOBP
ant.jar=$(build-classpath ant)
servlet-api.jar=$(build-classpath apache-tomcat-apis/tomcat-servlet2.4-api.jar)
jsp-api.jar=$(build-classpath apache-tomcat-apis/tomcat-jsp2.0-api.jar)
tools.jar=%{java.home}/lib/tools.jar
commons-el.jar=$(build-classpath commons-el)
commons-logging.jar=$(build-classpath commons-logging)
junit.jar=$(build-classpath junit)
compile.debug=on
compile.deprecation=off
compile.optimize=off
compile.source=1.4
compile.target=1.4
jasper-compiler-jdt.jar=$(build-classpath ecj)
EOBP
    ant -Djava.home="%{java_home}" -Dbuild.compiler="modern" javadoc build-main
popd
# create jasper-eclipse jar
mkdir -p org.apache.jasper
pushd org.apache.jasper
unzip -qq ../apache-tomcat-%{version}-src/jasper/build/shared/lib/jasper-compiler.jar
unzip -qq ../apache-tomcat-%{version}-src/jasper/build/shared/lib/jasper-runtime.jar \
  -x META-INF/MANIFEST.MF org/apache/jasper/compiler/Localizer.class
unzip -qq %{_javadir}/ecj.jar -x META-INF/MANIFEST.MF
cp -p %{SOURCE7} META-INF/MANIFEST.MF
rm -f plugin.properties plugin.xml about.html jdtCompilerAdapter.jar META-INF/eclipse.inf
zip -qq -r ../org.apache.jasper_5.5.17.v200706111724.jar .
popd

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_javadir}

# javadoc
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}-%{version}
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/jasper
    %{__cp} -pr build/javadoc/* \
        ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}-%{version}
    %{__ln_s} %{name}-%{version} ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}
popd

%{__cp} -p org.apache.jasper_5.5.17.v200706111724.jar ${RPM_BUILD_ROOT}%{_javadir}/%{name}-%{version}.jar

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc %{packdname}/build/LICENSE
%{_javadir}/%{name}-*.jar

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

%changelog
* Thu Feb 04 2010 Andrew Overholt <overholt@redhat.com> 5.5.28-3
- Trim BRs/Rs.

* Thu Feb 04 2010 Andrew Overholt <overholt@redhat.com> 5.5.28-2
- Use new servlet and JSP API JAR locations.

* Thu Dec 17 2009 Jeff Johnston <jjohnstn@redhat.com> 5.5.28-1
- Split Jasper out of tomcat5 SRPM.
