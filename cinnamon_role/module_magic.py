# Copyright (c) 2016 Ryan Rossiter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
