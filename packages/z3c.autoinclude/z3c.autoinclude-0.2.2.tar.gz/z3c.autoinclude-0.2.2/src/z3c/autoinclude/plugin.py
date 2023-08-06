import os
from pkg_resources import iter_entry_points
from pkg_resources import resource_filename
from z3c.autoinclude.utils import DistributionManager
from z3c.autoinclude.utils import distributionForDottedName

class PluginFinder(DistributionManager):
    def __init__(self, platform_dottedname):
        self.context = distributionForDottedName(platform_dottedname)
        self.dottedname = platform_dottedname

    def includableInfo(self, include_candidates):
        includable_info = {}

        for plugin_distribution in find_plugins(self.dottedname):
            include_finder = DistributionManager(plugin_distribution)
            for plugin_dottedname in include_finder.dottedNames():
                groups = zcml_to_include(plugin_dottedname, include_candidates)
                for group in groups:
                    includable_info.setdefault(group, []).append(plugin_dottedname)
        return includable_info


def find_plugins(dotted_name):
    plugins = []
    for ep in iter_entry_points('z3c.autoinclude.plugin'):
        if ep.module_name == dotted_name:
            plugins.append(ep.dist)
    return plugins

def zcml_to_include(dotted_name, zcmlgroups=None):
    if zcmlgroups is None:
        zcmlgroups = ('meta.zcml', 'configure.zcml', 'overrides.zcml')
    
    includable_info = []

    for zcmlgroup in zcmlgroups:
        filename = resource_filename(dotted_name, zcmlgroup)
        if os.path.isfile(filename):
            includable_info.append(zcmlgroup)
    return includable_info
