import os
import sys
import pdb
import shutil
from optparse import OptionParser

from pkg_resources import iter_entry_points
from pkg_resources import resource_filename
from pkg_resources import DistributionNotFound


def provide_skin(package, name, skin_path="skin"):
    """create skin information and return it"""
    skin = dict(
            name=name,
            package=package,
            skin_path=resource_filename(package, skin_path))
    return skin


def copy_skin(skin_path, target):
    """copy a skin to a target directory"""
    if os.path.exists(target):
        raise RuntimeError("Target path %s already exists." % target)

    shutil.copytree(skin_path, target, symlinks=False)

def iter_vudo_skins():
    """iterator for vudo skins"""
    for ep in iter_entry_points(group="vudo.skin"):
        try:
            skin_plugin = ep.load()
        except DistributionNotFound, e:
            print "*** the skin '%s' provided by module '%s' could not be "\
            "load because of missing dependencies: %s" % (
                    ep.name, ep.module_name, e)
            import pdb; pdb.set_trace() 
            continue
        if callable(skin_plugin):
            yield skin_plugin()


def do_list_skins():
    """List all skins in the system"""
    print "skin templates available:"
    total = 0
    print
    print "Skin Name, Package name, Skin path"
    print "-"*80
    for skin in iter_vudo_skins():
        print "%(name)s, %(package)s, %(skin_path)s" % skin
        total += 1
    print "total %d templates." % total


def do_copy(skin_name, path):
    for skin in iter_vudo_skins():
        if skin["name"] == skin_name:
            skin_path = skin["skin_path"]
            print "copying skin %s (%s) to %s ..." % (skin_name, skin_path, path)
            copy_skin(skin_path, os.path.join(path, skin["name"]))
            break
    else:
        print >>sys.stderr, "Skin not found."

def do_symlink(skin_name, path):
    for skin in iter_vudo_skins():
        if skin["name"] == skin_name:
            skin_path = skin["skin_path"]
            target = os.path.join(path, skin["name"])
            print "Creating a symbolic link: '%s' -> %s ..." % (skin_path, target)
            os.symlink(skin_path, target)
            break
    else:
        print >>sys.stderr, "Skin not found."


def main():
    """vudoskin script entry point"""

    parser = OptionParser()
    parser.add_option("-d", "--debug", dest="debug", default=False,
            help="set debugging mode.")
    parser.add_option("-D", "--post-mortem", action="store_true",
            dest="postmortem", default=False,
            help="launch post-mortem pdb on exceptions")

    parser.add_option("-l", "--list", dest="list", action="store_true",
            help="list available skins in the system.")

    parser.add_option("-c", "--copy", dest="copy", action="store_true",
            help="Copy skin resources to local directory.")

    parser.add_option("-s", "--symlink", dest="symlink", action="store_true",
            help="Symlink skin directory to local directory (development mode).")

    parser.add_option("-p", "--local-skin-path", dest="path", type="string",
            default="skins",
            help="Specifies the local skin directory (default: 'skins')")

    parser.add_option("-n", "--skin-name", dest="name", type="string",
            help="list available skins in the system.")


    (options, args) = parser.parse_args()

    if options.copy and options.symlink:
        print >>sys.stderr, "Please choose either 'copy' or 'symlink'."
        sys.exit(10)

    if options.copy or options.symlink:
        if options.name is None:
            print >>sys.stderr, "Please specify a skin name."
            sys.exit(10)

        if not os.path.exists(options.path):
            print >>sys.stderr, "The local skin path '%s' does not exist, please specify a local skin directory." % options.path
            sys.exit(10)

    try:
        if options.list:
            do_list_skins()
            sys.exit(1)

        if options.copy:
            do_copy(options.name, options.path)

        if options.symlink:
            do_symlink(options.name, options.path)

    except Exception, e:
        print "Exception:", e
        if options.postmortem:
            e, m, tb = sys.exc_info()
            pdb.post_mortem(tb)
        raise
        
