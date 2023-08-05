#!/usr/bin/make -f
INSTALL   = /usr/bin/install -c

default: qemu-7 qemu-8 vde
	
qemu-7:
	@if [ ! -f qemu-0.7.2.tar.gz ] ; then \
		echo "downloading qemu" ;\
		wget -nv http://fabrice.bellard.free.fr/qemu/qemu-0.7.2.tar.gz ;\
	fi
	@if [ ! -f kqemu-0.7.2.tar.gz ] ; then \
		echo "downloading kqemu" ;\
		wget -nv http://fabrice.bellard.free.fr/qemu/kqemu-0.7.2.tar.gz ;\
	fi
	tar xzf qemu-0.7.2.tar.gz
	tar xzf kqemu-0.7.2.tar.gz -C qemu-0.7.2
	-@cd qemu-0.7.2 && ./configure --host-cc=gcc-3.3 --disable-gfx-check --cc=gcc-3.3 --target-list=i386-softmmu --prefix=../..
	-@cd qemu-0.7.2 && make
	
qemu-8:
	@if [ ! -f qemu-0.8.2.tar.gz ] ; then \
		echo "downloading qemu" ;\
		wget -nv http://fabrice.bellard.free.fr/qemu/qemu-0.8.2.tar.gz ;\
	fi
	tar xzf qemu-0.8.2.tar.gz
	-@cd qemu-0.8.2 && ./configure --host-cc=gcc-3.3 --disable-gfx-check --cc=gcc-3.3 --target-list=i386-softmmu --prefix=../..
	-@cd qemu-0.8.2 && make


vde:
	@if [ ! -d vde ] ; then \
		echo "downloading vde" ;\
		echo "when asked for a password, press return" ;\
		cvs -d:pserver:anonymous@vde.cvs.sourceforge.net:/cvsroot/vde login ;\
		cvs -z3 -d:pserver:anonymous@vde.cvs.sourceforge.net:/cvsroot/vde co -P vde ;\
	else \
		echo "updating vde" ;\
		echo "when asked for a password, press return" ;\
		cvs -d:pserver:anonymous@cvs.sourceforge.net:/cvsroot/vde login ;\
		-@cd vde && cvs -z3 -d:pserver:anonymous@cvs.sourceforge.net:/cvsroot/vde update ;\
	fi
	-@cd vde && autoreconf --install
	-@cd vde && ./configure
	-@cd vde && make

clean:
	rm -rf vde qemu-0.7.2 qemu-0.8.2

install-vde:
	@echo "installing tools to ../bin"
	${INSTALL} -m 755 vde/vde_switch ../bin
	${INSTALL} -m 755 vde/vde_plug ../bin
	${INSTALL} -m 755 vde/qemu/vdeq ../bin
	${INSTALL} -m 755 vde/dpipe ../bin

install-qemu7:
	@echo "installing tools to ../bin"
	-@cd qemu-0.7.2 && make install
	${INSTALL} -m 755 qemu-0.7.2/i386-softmmu/qemu ../bin/qemu-0.7.2
	@echo "run qemu-0.7.2/kqemu/install.sh to install kernel module (as root)"

install-qemu8:
	@echo "installing tools to ../bin"
	-@cd qemu-0.8.2 && make install
	${INSTALL} -m 755 qemu-0.8.2/i386-softmmu/qemu ../bin/qemu-0.8.2
	@echo "run qemu-0.8.2/kqemu/install.sh to install kernel module (as root)"

install: install-vde install-qemu
