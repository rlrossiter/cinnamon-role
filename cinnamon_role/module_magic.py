import inspect
import pkgutil

from tempest import api


def get_all_tempest_api_tests():
    packages = set(_import_packages(api))
    modules = set(_import_modules(packages))
    classes = set(_get_classes(modules))
    return classes


def _import_packages(mod):
    modules = [mod]
    for loader, name, is_pkg in pkgutil.walk_packages(mod.__path__):
        # Skip all of the admin tests, because those are wacky
        # from a user standpoint
        if 'admin' in name:
            continue
        if is_pkg:
            sub_pkg = loader.find_module(name).load_module(name)
            modules += _import_packages(sub_pkg)
    return modules


def _import_modules(packages):
    modules = []
    for package in packages:
        for loader, name, is_pkg in pkgutil.iter_modules(package.__path__):
            if is_pkg:
                continue
            modules.append(loader.find_module(name).load_module(name))
    return modules


def _get_classes(modules):
    classes = []
    for mod in modules:
        mod_classes = inspect.getmembers(mod, predicate=inspect.isclass)
        # inspect returns a tuple of (name, class_obj) for each class
        # it finds. We only want the classes
        mod_classes = [cls[1] for cls in mod_classes]
        classes += mod_classes

    return classes
