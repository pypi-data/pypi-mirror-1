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

    return [v for k, v in zcml_types.items() \
                 if os.path.exists(os.path.join(inner_dir, '%s.zcml' % k))]


def install(buildout=None):
    if buildout['buildout'].has_key('tractor-src-directory'):
        src_dirs = buildout['buildout']['tractor-src-directory'].split()
    elif os.path.exists('src'):
        src_dirs = ['src']
    else:
        return

    instance_part_name = ''
    for k, v in buildout.items():
        if v.has_key('zope2-location'):
            log.debug('found zope instance part at [%s]' % k)
            instance_part_name = k
            if not v.has_key('zcml'):
                buildout[k]['zcml'] = ''
            if not v.has_key('eggs'):
                buildout[k]['eggs'] = ''
            break

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
                log.debug('found an egg in %s' % egg_path)

                if buildout['buildout']['develop'].find(egg_path) == -1:
                    buildout['buildout']['develop'] += ' %s' % egg_path
                    log.debug("Added %s to develop section" % egg_path)

                if instance_part_name:
                    if buildout[instance_part_name]['eggs'].find(egg_name) == -1:
                        buildout[instance_part_name]['eggs'] += ' %s' % egg_name
                        log.debug("Added %s to the egg section" % egg_name)

                    if egg_name in zcml_tops:
                        log.debug("Defered a top zcml: %s" % egg_name)
                        zcml_tops_found[egg_name] = egg_path
                    else:
                        for zcml_type in  _find_zcml_files(egg_path):
                            zcml_slug = '%s%s' % (egg_name, zcml_type)
                            if buildout[instance_part_name]['zcml'].find(zcml_slug) == -1:
                                buildout[instance_part_name]['zcml'] +=  ' %s' % zcml_slug
                                log.debug("Added %s to the zcml section of [%s]" % (zcml_slug, instance_part_name))
    #now, handle the top zcml slugs
    if instance_part_name:
        #this is just for getting the right order
        top_eggs = [e for e in zcml_tops if e in zcml_tops_found.keys()]
        for egg_name in top_eggs:
            for zcml_type in _find_zcml_files(zcml_tops_found[egg_name]):
                zcml_slug = '%s%s' % (egg_name, zcml_type)
                if buildout[instance_part_name]['zcml'].find(zcml_slug) == -1:
                    buildout[instance_part_name]['zcml'] =  '%s %s' % (zcml_slug, buildout[instance_part_name]['zcml'])
                    log.debug("Added %s%s to the top of the zcml section of [%s]" % (zcml_slug, instance_part_name))
