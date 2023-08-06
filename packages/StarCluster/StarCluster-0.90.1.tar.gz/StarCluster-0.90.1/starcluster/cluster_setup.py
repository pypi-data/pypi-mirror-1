#!/usr/bin/env python

"""
cluster_setup.py
"""

import os
import shutil
import logging
import tempfile

from starcluster.starclustercfg import *
from templates.sgeprofile import sgeprofile_template
from templates.sgeinstall import sgeinstall_template
from templates.sge_pe import sge_pe_template

log = logging.getLogger('starcluster')

def setup_cluster_user(nodes):
    """ Create cluster user on all StarCluster nodes """
    log.info("Creating cluster user: %s" % CLUSTER_USER)
    for node in nodes:
        nconn = node['CONNECTION']
        nconn.execute('useradd -m -s `which %s` %s' % (CLUSTER_SHELL, CLUSTER_USER))

def setup_scratch(nodes):
    """ Configure scratch space on all StarCluster nodes """
    log.info("Configuring scratch space for user: %s" % CLUSTER_USER)
    for node in nodes:
        nconn = node['CONNECTION']
        nconn.execute('mkdir /mnt/%s' % CLUSTER_USER)
        nconn.execute('chown -R %(user)s:%(user)s /mnt/%(user)s' % {'user':CLUSTER_USER})
        nconn.execute('mkdir /scratch')
        nconn.execute('ln -s /mnt/%s /scratch' % CLUSTER_USER)

def setup_etc_hosts(nodes):
    """ Configure /etc/hosts on all StarCluster nodes"""
    log.info("Configuring /etc/hosts on each node")
    for node in nodes:
        conn = node['CONNECTION']
        host_file = conn.remote_file('/etc/hosts')
        print >> host_file, "# Do not remove the following line or programs that require network functionality will fail"
        print >> host_file, "127.0.0.1 localhost.localdomain localhost"
        for node in nodes:
            print >> host_file, "%(INTERNAL_IP)s %(INTERNAL_NAME)s %(INTERNAL_NAME_SHORT)s %(INTERNAL_ALIAS)s" % node 
        host_file.close()

def setup_passwordless_ssh(nodes):
    """ Properly configure passwordless ssh for CLUSTER_USER on all StarCluster nodes"""
    log.info("Configuring passwordless ssh for root")

    master = nodes[0]
    mconn = master['CONNECTION']

    # create local ssh key for root and copy to local tempdir
    # remove any old keys first
    mconn.execute('rm /root/.ssh/id_rsa*')
    mconn.execute('ssh-keygen -q -t rsa -f /root/.ssh/id_rsa -P ""')
    tempdir = tempfile.mkdtemp(prefix="starcluster-")
    temprsa = os.path.join(tempdir, 'id_rsa')
    temprsa_pub = os.path.join(tempdir, 'id_rsa.pub')
    mconn.get('/root/.ssh/id_rsa', temprsa)
    mconn.get('/root/.ssh/id_rsa.pub', temprsa_pub)

    # copy newly generated id_rsa for root to each node
    for node in nodes:
        conn = node['CONNECTION']
        conn.put(temprsa,'/root/.ssh/id_rsa')
        conn.put(temprsa_pub,'/root/.ssh/id_rsa.pub')
        conn.execute('chmod 400 /root/.ssh/id_rsa*')
        conn.execute('cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys')

    # no longer need the temp directory after copying over newly generated keys
    # leave for now to debug
    #shutil.rmtree(tempdir)

    # Now that root's passwordless ssh is setup:
    # 1. Make initial connections to all nodes to skip host key checking on first use.
    # 2. This populates /root/.ssh/known_hosts which is copied to CLUSTER_USER's
    # ~/.ssh directory below
    for node in nodes:
        mconn.execute('ssh -o "StrictHostKeyChecking=no" %(INTERNAL_IP)s hostname' % node)
        mconn.execute('ssh -o "StrictHostKeyChecking=no" %(INTERNAL_NAME)s hostname' % node)
        mconn.execute('ssh -o "StrictHostKeyChecking=no" %(INTERNAL_NAME_SHORT)s hostname' % node)
        mconn.execute('ssh -o "StrictHostKeyChecking=no" %(INTERNAL_ALIAS)s hostname' % node)

    log.info("Configuring passwordless ssh for user: %s" % CLUSTER_USER)
    # only needed on master, nfs takes care of the rest
    mconn.execute('mkdir -p /home/%s/.ssh' % CLUSTER_USER)
    pkfiles_list = ("/home/%(user)s/.ssh/id_rsa /home/%(user)s/.ssh/id_rsa.pub" % {'user':CLUSTER_USER}).split()
    # check to see if both private key files exist (ie key and public key)
    pkfiles_exist = [ eval(mconn.execute('test -f %s && echo "True" || echo "False"'%file)[0]) for file in pkfiles_list ]
    has_all_pkfiles = (pkfiles_exist.count(True) == len(pkfiles_list))
    pkfiles = zip(pkfiles_list, pkfiles_exist)

    if not has_all_pkfiles:
        # this handles the case of only id_rsa or id_rsa.pub existing (ie not both for whatever reason)
        # in this case we want to remove whichever exists by itself and generate new local rsa keys
        for file,exists in pkfiles:
            log.debug('Checking for orphaned private key file: %s | exists = %s' % (file, exists))
            if exists:
                log.debug('Removing orphaned private key file: %s' % file)
                mconn.execute('rm %s' % file)
        log.info("Generating local RSA ssh keys for user: %s" % CLUSTER_USER)
        mconn.execute('ssh-keygen -q -t rsa -f /home/%s/.ssh/id_rsa -P ""' % CLUSTER_USER)
    else:
        # existing rsa key with matching pub key exists, no need to regenerate
        log.info("Using existing RSA ssh keys found for user: %s" % CLUSTER_USER)
        
    mconn.execute('cp /root/.ssh/authorized_keys /home/%s/.ssh/' % CLUSTER_USER)
    mconn.execute('cp /root/.ssh/known_hosts /home/%s/.ssh/' % CLUSTER_USER)
    mconn.execute('chown -R %(user)s:%(user)s /home/%(user)s/.ssh' % {'user':CLUSTER_USER})
    mconn.execute('chmod 400 /home/%s/.ssh/id_rsa*' % CLUSTER_USER)
    mconn.execute('cat /home/%(user)s/.ssh/id_rsa.pub >> /home/%(user)s/.ssh/authorized_keys' % {'user':CLUSTER_USER})

def setup_ebs_volume(nodes):
    """ Mount EBS volume, if specified, in ~/.starclustercfg to /home"""
    # setup /etc/fstab on master to use block device if specified
    log.info("Mounting EBS volume %s on /home..." % ATTACH_VOLUME)
    if ATTACH_VOLUME is not None and VOLUME_PARTITION is not None:
        mconn = nodes[0]['CONNECTION']
        master_fstab = mconn.remote_file('/etc/fstab', mode='a')
        print >> master_fstab, "%s /home ext3 noauto,defaults 0 0 " % VOLUME_PARTITION
        master_fstab.close()
        mconn.execute('mount /home')

def setup_nfs(nodes):
    """ Share /home and /opt/sge6 via nfs to all nodes"""
    log.info("Configuring NFS...")

    master = nodes[0]
    mconn = master['CONNECTION']

    # copy fresh sge installation files to /opt/sge6 and make CLUSTER_USER the owner
    mconn.execute('cp -r /opt/sge6-fresh /opt/sge6')
    mconn.execute('chown -R %(user)s:%(user)s /opt/sge6' % {'user': CLUSTER_USER})

    # setup /etc/exports and start nfsd on master node
    nfs_export_settings = "(async,no_root_squash,no_subtree_check,rw)"
    etc_exports = mconn.remote_file('/etc/exports')
    for node in nodes:
        if node['NODE_ID'] != 0:
            etc_exports.write('/home/ ' + node['INTERNAL_NAME'] + nfs_export_settings + '\n')
            etc_exports.write('/opt/sge6 ' + node['INTERNAL_NAME'] + nfs_export_settings + '\n')
    etc_exports.close()
    
    mconn.execute('/etc/init.d/portmap start')
    mconn.execute('mount -t rpc_pipefs sunrpc /var/lib/nfs/rpc_pipefs/')
    mconn.execute('/etc/init.d/nfs start')
    mconn.execute('/usr/sbin/exportfs -r')
    mconn.execute('mount -t devpts none /dev/pts') # fix for xterm

    # setup /etc/fstab and mount /home and /opt/sge6 on each node
    for node in nodes:
        if node['NODE_ID'] != 0:
            nconn = node['CONNECTION']
            nconn.execute('/etc/init.d/portmap start')
            nconn.execute('mkdir /opt/sge6')
            nconn.execute('chown -R %(user)s:%(user)s /opt/sge6' % {'user':CLUSTER_USER})
            nconn.execute('echo "%s:/home /home nfs user,rw,exec 0 0" >> /etc/fstab' % master['INTERNAL_NAME'])
            nconn.execute('echo "%s:/opt/sge6 /opt/sge6 nfs user,rw,exec 0 0" >> /etc/fstab' % master['INTERNAL_NAME'])
            nconn.execute('mount /home')
            nconn.execute('mount /opt/sge6')
            nconn.execute('mount -t devpts none /dev/pts') # fix for xterm

def setup_sge(nodes):
    """ Install Sun Grid Engine with a default parallel environment on StarCluster"""
    log.info("Installing Sun Grid Engine...")

    # generate /etc/profile.d/sge.sh for each node
    for node in nodes:
        conn = node['CONNECTION']
        sge_profile = conn.remote_file("/etc/profile.d/sge.sh")
        arch = conn.execute("/opt/sge6/util/arch")[0]

        print >> sge_profile, sgeprofile_template  % {'arch': arch}
        sge_profile.close()

    # setup sge auto install file
    master = nodes[0]
    mconn = master['CONNECTION']

    admin_list = ''
    for node in nodes:
        admin_list = admin_list + " " +node['INTERNAL_NAME']

    exec_list = admin_list
    submit_list = admin_list
    ec2_sge_conf = mconn.remote_file("/opt/sge6/ec2_sge.conf")

    # todo: add sge section to config values for some of the below
    print >> ec2_sge_conf, sgeinstall_template % (admin_list, exec_list, submit_list)
    ec2_sge_conf.close()

    # installs sge in /opt/sge6 and starts qmaster and schedd on master node
    mconn.execute('cd /opt/sge6 && TERM=rxvt ./inst_sge -m -x -auto ./ec2_sge.conf', silent=True, only_printable=True)

    # set all.q shell to bash
    mconn.execute('source /etc/profile && qconf -mattr queue shell "/bin/bash" all.q')

    # create sge parallel environment
    # first iterate through each machine and count the number of processors
    num_processors = 0
    for node in nodes:
        conn = node['CONNECTION']
        num_procs = int(conn.execute('cat /proc/cpuinfo | grep processor | wc -l')[0])
        num_processors += num_procs

    parallel_environment = mconn.remote_file("/tmp/pe.txt")
    print >> parallel_environment, sge_pe_template % num_processors
    parallel_environment.close()
    mconn.execute("source /etc/profile && qconf -Ap %s" % parallel_environment.name)

    mconn.execute('source /etc/profile && qconf -mattr queue pe_list "orte" all.q')

    #todo cleanup /tmp/pe.txt 
    log.info("Done Configuring Sun Grid Engine")

def main(nodes):
    """Start cluster configuration"""
    setup_ebs_volume(nodes)
    setup_cluster_user(nodes)
    setup_scratch(nodes)
    setup_etc_hosts(nodes)
    setup_nfs(nodes)
    setup_passwordless_ssh(nodes)
    setup_sge(nodes)
