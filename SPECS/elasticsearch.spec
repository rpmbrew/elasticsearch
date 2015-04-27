#%%global reltag .Beta1
%global namedversion %{version}%{?reltag}
%global _docdir_fmt %{name}

Name:          elasticsearch
Version:       1.5.1
Release:       0%{?reltag}%{?dist}
Summary:       Open source, flexible, distributed search and analytics engine
License:       ASL 2.0
URL:           http://www.elasticsearch.org/
# wget https://github.com/elasticsearch/elasticsearch/archive/v1.4.4.tar.gz
# repacked by repack.sh 
Source0:       %{name}-%{namedversion}-fedora.tar.xz
Source1:       repack.sh
Source2:       %{name}.service.in
Source3:       %{name}.in
Patch0:        %{name}-1.3.2-remove-sigar-service.patch
Patch1:        unbundleBase64.patch
Patch2:        localhostByDefault.patch
Patch3:        netty-version.patch


BuildRequires: netty3
BuildRequires: java-base64 >= 2.3.8-7
BuildRequires: mvn(org.apache.maven.plugins:maven-dependency-plugin)
BuildRequires: mvn(com.carrotsearch:hppc)
BuildRequires: mvn(com.fasterxml.jackson.core:jackson-core)
BuildRequires: mvn(com.fasterxml.jackson.dataformat:jackson-dataformat-cbor)
BuildRequires: mvn(com.fasterxml.jackson.dataformat:jackson-dataformat-smile)
BuildRequires: mvn(com.fasterxml.jackson.dataformat:jackson-dataformat-yaml)
BuildRequires: mvn(com.github.spullara.mustache.java:compiler)
BuildRequires: mvn(com.google.guava:guava)
BuildRequires: mvn(com.ning:compress-lzf)
BuildRequires: mvn(com.spatial4j:spatial4j)
BuildRequires: mvn(com.tdunning:t-digest)
BuildRequires: mvn(com.vividsolutions:jts)
BuildRequires: mvn(joda-time:joda-time)
BuildRequires: mvn(net.java.dev.jna:jna)
BuildRequires: mvn(org.antlr:antlr-runtime)
BuildRequires: mvn(org.codehaus.groovy:groovy)
BuildRequires: mvn(org.joda:joda-convert)
BuildRequires: mvn(org.mvel:mvel2)
BuildRequires: mvn(org.slf4j:slf4j-api)
BuildRequires: mvn(org.sonatype.oss:oss-parent:pom:)
BuildRequires: mvn(log4j:log4j:1.2.17)
BuildRequires: mvn(log4j:apache-log4j-extras)
BuildRequires: mvn(org.apache.lucene:lucene-analyzers-common)
BuildRequires: mvn(org.apache.lucene:lucene-codecs)
BuildRequires: mvn(org.apache.lucene:lucene-core)
BuildRequires: mvn(org.apache.lucene:lucene-expressions)
BuildRequires: mvn(org.apache.lucene:lucene-highlighter)
BuildRequires: mvn(org.apache.lucene:lucene-join)
BuildRequires: mvn(org.apache.lucene:lucene-memory)
BuildRequires: mvn(org.apache.lucene:lucene-queries)
BuildRequires: mvn(org.apache.lucene:lucene-queryparser)
BuildRequires: mvn(org.apache.lucene:lucene-spatial)
BuildRequires: mvn(org.apache.lucene:lucene-suggest)

%if 0
# Test deps
BuildRequires: mvn(com.carrotsearch.randomizedtesting:junit4-maven-plugin)
BuildRequires: mvn(com.carrotsearch.randomizedtesting:junit4-ant)
BuildRequires: mvn(com.carrotsearch.randomizedtesting:randomizedtesting-runner)
BuildRequires: mvn(de.thetaphi:forbiddenapis)
BuildRequires: mvn(org.hamcrest:hamcrest-all)
BuildRequires: mvn(org.apache.lucene:lucene-test-framework)
BuildRequires: mvn(org.apache.httpcomponents:httpclient)
%endif

BuildRequires: maven-local
#service build
BuildRequires: systemd
# not added by autogenerated stuff
Requires: lucene-sandbox
Requires: snakeyaml
# xmvn do not set up versions
Requires: java-base64 >= 2.3.8-7
# service setup
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
# user and group creation
Requires(pre): shadow-utils

BuildArch:     noarch

%description
Elasticsearch is a search server based on Lucene. It provides a distributed, 
multitenant-capable full-text search engine with a RESTful web interface and 
schema-free JSON documents. Elasticsearch is developed in Java and is released 
as open source under the terms of the Apache License.

It is a flexible and powerful open source, distributed, real-time 
search and analytics engine. 

Architected from the ground up for use in distributed environments where 
reliability and scalability are must haves, Elasticsearch gives you the ability 
to move easily beyond simple full-text search. 

Through its robust set of APIs and query DSLs, plus clients for the most popular 
programming languages, Elasticsearch delivers on the near limitless promises of 
search technology.

%package javadoc
Summary:       Javadoc for %{name}

%description javadoc
This package contains javadoc for %{name}.

%prep
%autosetup -n elasticsearch-%{namedversion} -p0
# Cleanup
find . -name "*.class" -print -delete
find . -name "*.jar" -print -delete
find . -name "*.bat" -print -delete
find . -name "*.exe" -print -delete
# Unused/unavailable plugins
%pom_remove_plugin de.thetaphi:forbiddenapis
%pom_remove_plugin com.mycila:license-maven-plugin
%pom_remove_plugin org.vafer:jdeb
%pom_remove_plugin :maven-shade-plugin
%pom_remove_plugin :maven-source-plugin
%pom_remove_plugin :rpm-maven-plugin
%pom_remove_plugin com.carrotsearch.randomizedtesting:junit4-maven-plugin
%pom_remove_plugin :buildnumber-maven-plugin
%pom_remove_plugin :maven-dependency-plugin
%pom_remove_plugin :maven-assembly-plugin
#%%pom_add_dep com.carrotsearch.randomizedtesting:junit4-ant::test
%pom_add_dep net.iharder:base64

# Disable test task
%pom_xpath_remove "pom:build/pom:plugins/pom:plugin[pom:artifactId = 'maven-antrun-plugin']/pom:executions/pom:execution[pom:id = 'tests']"

# package org.antlr.runtime.tree does not exist
%pom_add_dep org.antlr:antlr-runtime

# do not require lucene 4.10.4 yet
sed -i s/LUCENE_4_10_4/LUCENE_4_10_3/ src/main/java/org/elasticsearch/Version.java

%pom_remove_dep org.fusesource:sigar
rm -rfv src/main/java/org/elasticsearch/monitor/sigar \
 src/main/java/org/elasticsearch/monitor/process/SigarProcessProbe.java \
 src/main/java/org/elasticsearch/monitor/network/SigarNetworkProbe.java \
 src/main/java/org/elasticsearch/monitor/os/SigarOsProbe.java \
 src/main/java/org/elasticsearch/monitor/fs/SigarFsProbe.java

#removal of bundled class
rm -vf src/main/java/org/elasticsearch/common/Base64.java

%build
%mvn_file : %{name}
%mvn_build -f


%install
%mvn_install
# the target/bin/elasticsearch.in.sh is not packed, as it do not honor packaging guidelines
# proper mixture of it and rpm based launcher will be subject of further work
# todo, discover origin of elasticsearch launcher script, does not seems to be based on in file
# the in file seems to be only strangely included
mkdir -p $RPM_BUILD_ROOT/%{_libexecdir}/
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}/
cat %{SOURCE2} | sed  "s;@LAUNCHER@;%{_libexecdir}/%{name};g" | sed  "s;@USER@;%{name};g"  > $RPM_BUILD_ROOT/%{_unitdir}/%{name}.service
# because of bugs in set_flags/options and custom code, using .in file instead of %%jpackage_script 
cat %{SOURCE3} | sed "s;@NAME@;%{name};g" | sed "s;@VLIB@;%{_sharedstatedir};g" >$RPM_BUILD_ROOT/%{_libexecdir}/%{name}
chmod 755 $RPM_BUILD_ROOT/%{_libexecdir}/%{name}
# setup config templates target dirs
mkdir -p $RPM_BUILD_ROOT/%{_sharedstatedir}/%{name}/conf/
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}
# setup config files in /etc/elasticsearch
cp config/%{name}.yml $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}
cp config/logging.yml $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}
# they are 755 by defualt in sources
chmod 644 $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/*.yml
# link them to ES home
ln -s %{_sysconfdir}/%{name}/%{name}.yml $RPM_BUILD_ROOT/%{_sharedstatedir}/%{name}/conf/
ln -s %{_sysconfdir}/%{name}/logging.yml  $RPM_BUILD_ROOT/%{_sharedstatedir}/%{name}/conf/


%pre
# add the elasticsearch user and group
getent group  %{name} >/dev/null || %{_sbindir}/groupadd -r %{name}
getent passwd %{name} >/dev/null || %{_sbindir}/useradd -r -g %{name} -d %{_sharedstatedir}/%{name} -s %{_sbindir}/nologin \
    -c "Elastic Search shared service user" elasticsearch
exit 0

%post
# install but don't activate
%systemd_post %{name}.service


%preun
%systemd_preun %{name}.service


%postun
%systemd_postun_with_restart %{name}.service 
# %%systemd_postun %%{name}.service 

%files -f .mfiles
%license LICENSE.txt NOTICE.txt
%doc README.textile CONTRIBUTING.md TESTING.asciidoc
%{_libexecdir}/%{name}
%{_sysconfdir}/%{name}
%{_unitdir}/%{name}.service
%attr(755, %{name}, %{name}) %{_sharedstatedir}/%{name}
%config(noreplace) %{_sharedstatedir}/%{name}/conf/%{name}.yml
%config(noreplace) %{_sharedstatedir}/%{name}/conf/logging.yml

%files javadoc -f .mfiles-javadoc
%license LICENSE.txt NOTICE.txt

%changelog
* Mon Apr 20 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 1.5.1-0
- update to latest upstream version

* Mon Feb 16 2015 Jiri Vanek <jvanek@redhat.com> - 1.4.4-0
- initial build