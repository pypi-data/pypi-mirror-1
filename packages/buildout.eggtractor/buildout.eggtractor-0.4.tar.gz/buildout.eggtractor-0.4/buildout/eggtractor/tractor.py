import os
import sys
import logging


log = logging.getLogger('buildout.eggtractor')


def _find_zcml_files(package_path):

    mod_names  = os.path.basename(package_path).split('.')

    source_dir = os.path.join(package_path, 'src')
    if not os.path.exists(source_dir):
        source_dir = package_path

    inner_dir = os.path.join(source_dir, *mod_names)
    zcml_types = {'meta': '-meta', 'configure': '', 'overrides': '-overrides'}

    return [v for k, v in zcml_types.items()
              if os.path.exists(os.path.join(inner_dir, '%s.zcml' % k))]


def install(buildout=None):
    if 'tractor-src-directory' in buildout['buildout']:
        src_dirs = buildout['buildout']['tractor-src-directory'].split()
    elif os.path.exists('src'):
        src_dirs = ['src']
    else:
        return

    instance_part_names = []
    for k, v in buildout.items():
        if v.get('recipe') == 'plone.recipe.zope2instance':
            log.debug('Found Zope instance part at [%s]' % k)
            instance_part_names.append(k)
            if 'zcml' not in v:
                buildout[k]['zcml'] = ''
            if 'eggs' not in v:
                buildout[k]['eggs'] = ''

    zcml_tops = []
    if buildout['buildout'].has_key('tractor-zcml-top'):
        zcml_tops = buildout['buildout']['tractor-zcml-top'].split()
    zcml_tops.reverse()

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

                for name in instance_part_names:
                    if egg_name not in buildout[name]['eggs']:
                        buildout[name]['eggs'] += '\n%s' % egg_name
                        log.debug("Added %s to the egg section of [%s]" % (egg_name, name))

                    if egg_name in zcml_tops:
                        log.debug("Defered a top zcml: %s" % egg_name)
                        zcml_tops_found[egg_name] = egg_path
                    else:
                        for zcml_type in _find_zcml_files(egg_path):
                            zcml_slug = '%s%s' % (egg_name, zcml_type)
                            # If the meta or override package include is found
                            # first, a simple test for zcml_slug would identify
                            # the configure include as already being in the list
                            if '%s ' % zcml_slug not in buildout[name]['zcml']:
                                buildout[name]['zcml'] +=  ' %s' % zcml_slug
                                log.debug("Added %s to the zcml section of [%s]" % (zcml_slug, name))
    #now, handle the top zcml slugs
    for name in instance_part_names:
        #this is just for getting the right order
        top_eggs = [e for e in zcml_tops if e in zcml_tops_found.keys()]
        for egg_name in top_eggs:
            for zcml_type in _find_zcml_files(zcml_tops_found[egg_name]):
                zcml_slug = '%s%s' % (egg_name, zcml_type)
                if zcml_slug not in buildout[name]['zcml']:
                    buildout[name]['zcml'] =  '%s %s' % (zcml_slug, buildout[name]['zcml'])
                    log.debug("Added %s%s to the top of the zcml section of [%s]" % (zcml_slug, name))
