import os
import sys
import logging

log = logging.getLogger('buildout.eggtractor')


def find_zcml_files(package_path):
    """Get configure.zcml, meta.zcml and overrides.zcml
    if any from package path.
    """

    mod_names  = os.path.basename(package_path).split('.')

    source_dir = os.path.join(package_path, 'src')
    if not os.path.exists(source_dir):
        source_dir = package_path

    inner_dir = os.path.join(source_dir, *mod_names)
    zcml_types = {'meta': '-meta', 'configure': '', 'overrides': '-overrides'}

    return [v for k, v in zcml_types.items()
              if os.path.exists(os.path.join(inner_dir, '%s.zcml' % k))]


def add_egg_to_part(buildout, part, egg):
    """Add the egg to the eggs option of the part
    """

    if 'eggs' not in buildout[part]:
        buildout[part]['eggs'] = ''

    if egg not in buildout[part]['eggs']:
        buildout[part]['eggs'] += '\n%s' % egg
        log.debug("Added %s to the egg section of [%s]" % (egg, part))


def add_egg_to_zcml(buildout, part, egg_path, egg_name, top=False):
    """Add the zcml slugs to the zcml option of the part
    """

    if buildout['buildout'].get('tractor-autoload-zcml', None) == 'false':
        return 

    if 'zcml' not in buildout[part]:
        buildout[part]['zcml'] = ''

    for zcml in find_zcml_files(egg_path):
        slug = '%s%s' % (egg_name, zcml)
        if '%s ' % slug not in buildout[part]['zcml']:
            if top:
                buildout[part]['zcml'] =  '%s %s' % (slug, buildout[part]['zcml'])
            else:
                buildout[part]['zcml'] +=  ' %s' % slug
            log.debug("Added %s to the zcml section of [%s]" % (slug, part))


def install(buildout=None):
    if 'tractor-src-directory' in buildout['buildout']:
        src_dirs = buildout['buildout']['tractor-src-directory'].split()
    elif os.path.exists('src'):
        src_dirs = ['src']
    else:
        return

    part_names = []
    if 'tractor-target-parts' in buildout['buildout']:
        part_names = [n for n in buildout['buildout']['tractor-target-parts'].split() if n in buildout]
    else:
        for k, v in buildout.items():
            if v.get('recipe') == 'plone.recipe.zope2instance':
                log.debug('Found Zope instance part at [%s]' % k)
                part_names.append(k)

    zcml_tops = []
    if 'tractor-zcml-top' in buildout['buildout']:
        zcml_tops = buildout['buildout']['tractor-zcml-top'].split()

    zcml_tops_found = {}
    for src_dir in src_dirs:
        for egg_name in os.listdir(src_dir):
            egg_path = os.path.join(src_dir, egg_name)
            #is it really an egg ?
            if os.path.exists(os.path.join(egg_path, 'setup.py')):
                log.debug('Found an egg in %s' % egg_path)

                if egg_path not in buildout['buildout']['develop']:
                    buildout['buildout']['develop'] += '\n%s' % egg_path
                    log.debug("Added %s to develop section" % egg_path)

                for name in part_names:
                    add_egg_to_part(buildout, name, egg_name)
                    if egg_name in zcml_tops:
                        log.debug("Defered a top zcml: %s" % egg_name)
                        zcml_tops_found[egg_name] = egg_path
                    else:
                        add_egg_to_zcml(buildout, name, egg_path, egg_name) 

    #this is just for getting the right order
    top_eggs = [e for e in zcml_tops if e in zcml_tops_found.keys()]
    top_eggs.reverse()
    #now, handle the top zcml slugs
    for name in part_names:
        for egg_name in top_eggs:
            egg_path = zcml_tops_found[egg_name]
            add_egg_to_zcml(buildout, name, egg_path, egg_name, top=True)

