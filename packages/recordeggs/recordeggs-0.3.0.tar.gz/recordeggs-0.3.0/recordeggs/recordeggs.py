#! /usr/bin/env python
"""Incredibly dumb script to process the output of easy_install and create install script

This captures the files download and creates an "egg-source" directory into which the 
source files are (re-downloaded).  A file is written which puts the packages in the 
order in which they are downloaded.

Note:
    Currently TurboGears 2.0 has a failing dependency that cannot properly 
    import easy_install's own code due to the assumption in the code that the 
    ez_setup.py module is always available.  This file is available from
    
        http://peak.telecommunity.com/dist/ez_setup.py
    
    but needs to be on the local path to be usable.

You would normally use a specific version for your original install as well, i.e.
your command-line would look like this:

    recordeggs -r ../egg-sources -i http://www.turbogears.org/2.0/downloads/2.0.1/index tg.devtools
"""
usage = """
    %prog -r [options] egg_dir [easy_install_options]
or:
    %prog -p [options] egg_dir

Intended for use with VirtualEnv, this script records the packages 
downloaded and replays the packages into another VirtualEnv 
environment in an attempt to replicate a dev environment for live 
deployments."""
import os,sys,urllib,logging,subprocess,datetime,optparse
log = logging.getLogger( 'recordeggs' )

INSTALL_TEMPLATE = 'easy_install -f %(sources)s -H "" -N -Z %(sources)s/%(file)s\n'

def record( sources, *args ):
    if not os.path.isdir( sources ):
        os.mkdir( sources )
    def shell_escape( x ):
        if '"' in x:
            x = x.replace( '"', '\\"')
        return '"'+x+'"'
    escaped_args = ' '.join( [shell_escape(x) for x in  args] )
    command = 'easy_install %s'%( escaped_args )
    log.info( 'Running: %s', command )
    process = subprocess.Popen(
        # TODO: shell-escape args...
        command,
        shell=True,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )
    log.warn( 'Beginning installation (this will take a while!)...' )
    stdout,stderr = process.communicate()
    to_install = []
    for line in stdout.splitlines() + stderr.splitlines():
        if line.startswith( 'Downloading ' ):
            fluff,url = line.strip().split( ' ', 1 )
            file = url.split( '/' )[-1]
            if '#' in file:
                file,marker = file.split( '#', 1 )
            #TODO: clean file-name...
            urllib.urlretrieve( url, os.path.join( sources, file ))
            to_install.append( 
                file 
            )
    sys.stdout.write( stdout )
    sys.stdout.write( stderr )
    script_file = os.path.join( sources, 'playbackeggs.list' )
    fh = open( script_file,'a')
    fh.write( '# %s %s %s\n'%( 
        datetime.datetime.now().isoformat(),
        shell_escape( sources ),
        escaped_args,
    ))
    for file in to_install:
        fh.write( '%s\n'%(file,))
    fh.close()
    log.info( 'Write script to %s', script_file )

def playback( sources ):
    if not os.environ.get( 'VIRTUAL_ENV' ):
        if os.isatty( sys.stdout.fileno() ):
            if not raw_input( """Do not appear to be within VirtualEnv, continue (y/n)? """).lower().startswith('y'):
                sys.exit( 1 )
        else:
            log.error( """Not within a virtualenv!""" )
            sys.exit( 1 )
    script_file = os.path.join( sources, 'playbackeggs.list' )
    if not os.path.isfile( script_file ):
        log.error( """No script file %s found""", script_file )
    lines = open( script_file )
    for line in lines:
        if not line.startswith( '#' ):
            file = line.strip()
            log.info( 'Installing: %s', file )
            if subprocess.call(
                INSTALL_TEMPLATE % locals(),
                shell=True,
            ):
                log.error( """Failure installing: %s""", file )

def main():
    logging.basicConfig( level=logging.INFO )
    parser = optparse.OptionParser( usage=usage )
    parser.disable_interspersed_args()
    parser.add_option(
        "-r", "--record", 
        dest="record", 
        default=True,
        action="store_true",
        help="Record script (default)", 
    )
    parser.add_option(
        "-p", "--playback", 
        dest="record", 
        action="store_false",
        help="Playback script", 
    )
    (options, args) = parser.parse_args()

    if not args:
        parser.print_help()
    else:
        if options.record:
            record( *args )
        else:
            playback( *args )

if __name__ == "__main__":
    main()
