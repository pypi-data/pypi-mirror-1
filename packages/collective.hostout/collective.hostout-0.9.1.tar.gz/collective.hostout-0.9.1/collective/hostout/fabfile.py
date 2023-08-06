import os
from os.path import join, basename, dirname

def createuser(buildout_user='buildout'):
    "Creates a user account to run the buildout in"
    #keyname="buildout_dsa.%s"%(buildout_host)
    #if not os.path.exists(keyname):
    if True:
        sudo('test -d ~$(buildout_user) || adduser $(buildout_user)')
        sudo('test -d ~$(buildout_user)/.ssh || mkdir ~$(buildout_user)/.ssh;')
        sudo('(chmod 700 ~$(buildout_user)/.ssh; touch ~$(buildout_user)/.ssh/authorized_keys)')
        sudo('chmod 600 ~$(buildout_user)/.ssh/authorized_keys')
        #run("rm -f /tmp/buildout_dsa")
        #run("ssh-keygen -t dsa -N '' -f /tmp/buildout_dsa")
        #run('rm ~$(buildout_user)/.ssh/buildout_dsa.pub')
        #try:
        #    download('/tmp/buildout_dsa','buildout_dsa')
        #    download('/tmp/buildout_dsa.pub','buildout_dsa.pub')
        #except:
        #    pass
        sudo('cp ~$(buildout_user)/.ssh/authorized_keys ~$(buildout_user)/.ssh/authorized_keys.bak')
        sudo('cat /tmp/buildout_dsa.pub >> ~$(buildout_user)/.ssh/authorized_keys')
    set(fab_key_filename=keyname)


def predeploy(hostout):
    "install buildout and its dependencies"
    #run('export http_proxy=localhost:8123') # TODO get this from setting

    set(dist_dir = hostout.getDownloadCache(),
        unified='Plone-3.2.1r3-UnifiedInstaller',
        unified_url='http://launchpad.net/plone/3.2/3.2.1/+download/Plone-3.2.1r3-UnifiedInstaller.tgz',
        )

    sudo('mkdir -p $(dist_dir)/dist && sudo chown -R $(effectiveuser) $(dist_dir)')
    sudo('mkdir -p %(dc)s && sudo chown $(effectiveuser) %(dc)s'% dict(dc=hostout.getEggCache()))

    #Download the unified installer if we don't have it
    sudo('test -f $(buildout_dir)/bin/buildout || \
         test -f $(dist_dir)/$(unified).tgz || \
         ( cd /tmp && \
         wget  --continue $(unified_url) && \
         sudo mv /tmp/$(unified).tgz $(dist_dir)/$(unified).tgz && \
         sudo chown $(effectiveuser) $(dist_dir)/$(unified).tgz \
         ) \
         ')
    # untar and run unified installer
    sudo('test -f $(buildout_dir)/bin/buildout || \
          (cd /tmp && \
          tar -xvf $(dist_dir)/$(unified).tgz && \
          test -d /tmp/$(unified) && \
          cd /tmp/$(unified) && \
          sudo mkdir -p  $(install_dir) && \
          sudo ./install.sh --target=$(install_dir) --instance=$(instance) --user=$(effectiveuser) --nobuildout standalone && \
          sudo chown -R $(effectiveuser) $(install_dir)/$(instance))')

    for cmd in hostout.getPreCommands():
        sudo('sh -c "%s"'%cmd)


#TODO Need to hook into init.d
#http://www.webmeisterei.com/friessnegger/2008/06/03/control-production-buildouts-with-supervisor/
#cd /etc/init.d/
#ln -s INSTANCE_HOME/bin/supervisord project-supervisord
#ln -s INSTANCE_HOME/bin/supervisorctl project-supervisorctl
#update-rc.d project-supervisord defaults


def dodeploy(hostout):
    "deploy the package of changed cfg files"

    #need to send package. cycledown servers, install it, run buildout, cycle up servers

    for pkg in hostout.localEggs():
        tmp = join('/tmp', basename(pkg))
        tgt = join(hostout.getDownloadCache(), 'dist', basename(pkg))
        try:
            sudo('test -f %s'%tgt)
        except:
            put(pkg, tmp)
            sudo("mv %s %s"%(tmp,tgt))
            sudo('chown $(effectiveuser) %s' % tgt)

    package=hostout.getHostoutPackage()
    tmp = join('/tmp', basename(package))
    tgt = join(hostout.getDownloadCache(), basename(package))

    try:
        sudo('test -f %s'%tgt)
    except:
        put(package, tmp)
        sudo("mv %s %s"%(tmp,tgt))
        sudo('chown $(effectiveuser) %s' % tgt)

    set(
        #fab_key_filename="buildout_dsa",
        dist_dir=hostout.dist_dir,
        install_dir=hostout.remote_dir,
        hostout_file=hostout.getHostoutFile(),
    )

    #need a way to make sure ownership of files is ok
    sudo('tar --no-same-permissions --no-same-owner --overwrite --owner $(effectiveuser) -xvf %s --directory=$(install_dir)' % tgt)
#    if hostout.getParts():
#        parts = ' '.join(hostout.getParts())
 #       sudo('sudo -u $(effectiveuser) sh -c "cd $(install_dir) && bin/buildout -c $(hostout_file) install %s"' % parts)
  #  else:
    #Need to set home var for svn to work
    sudo('sudo -u $(effectiveuser) sh -c "export HOME=~$(effectiveuser) && cd $(install_dir) && bin/buildout -c $(hostout_file)"')

#    run('cd $(install_dir) && $(reload_cmd)')
#    sudo('chmod 600 .installed.cfg')
#    sudo('find $(install_dir)  -type d -name var -exec chown -R $(effectiveuser) \{\} \;')
#    sudo('find $(install_dir)  -type d -name LC_MESSAGES -exec chown -R $(effectiveuser) \{\} \;')
#    sudo('find $(install_dir)  -name runzope -exec chown $(effectiveuser) \{\} \;')


def deploy(hostout):
    ""
    if hostout.password:
        set(fab_password=hostout.password)
    if hostout.identityfile:
        set(fab_key_filename=hostout.identityfile)
    set(
        fab_user=hostout.user,
        fab_hosts=[hostout.host],
        effectiveuser=hostout.effective_user,
        buildout_dir=hostout.remote_dir,
        install_dir=os.path.split(hostout.remote_dir)[0],
        instance=os.path.split(hostout.remote_dir)[1],
        download_cache=hostout.getDownloadCache()
    )

    predeploy(hostout)
    dodeploy(hostout)
    postdeploy(hostout)

def postdeploy(hostout):
    for cmd in hostout.getPostCommands():
        sudo('sh -c "%s"'%cmd)


