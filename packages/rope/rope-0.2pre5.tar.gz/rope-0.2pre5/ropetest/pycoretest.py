import os
import unittest

from ropetest import testutils
from rope.pycore import PyObject, ModuleNotFoundException, PythonFileRunner
from rope.project import Project

class PyCoreTest(unittest.TestCase):

    def setUp(self):
        super(PyCoreTest, self).setUp()
        self.project_root = 'sample_project'
        testutils.remove_recursively(self.project_root)
        self.project = Project(self.project_root)
        self.pycore = self.project.get_pycore()

    def tearDown(self):
        testutils.remove_recursively(self.project_root)
        super(PyCoreTest, self).tearDown()

    def test_simple_module(self):
        self.pycore.create_module(self.project.get_root_folder(), 'mod')
        result = self.pycore.get_module('mod')
        self.assertEquals(PyObject.get_base_type('Module'), result.type)
        self.assertEquals(0, len(result.get_attributes()))
    
    def test_nested_modules(self):
        pkg = self.pycore.create_package(self.project.get_root_folder(), 'pkg')
        mod = self.pycore.create_module(pkg, 'mod')
        package = self.pycore.get_module('pkg')
        self.assertEquals(PyObject.get_base_type('Module'), package.type)
        self.assertEquals(1, len(package.get_attributes()))
        module = package.get_attributes()['mod']
        self.assertEquals(PyObject.get_base_type('Module'), module.get_type())

    def test_package(self):
        pkg = self.pycore.create_package(self.project.get_root_folder(), 'pkg')
        mod = self.pycore.create_module(pkg, 'mod')
        result = self.pycore.get_module('pkg')
        self.assertEquals(PyObject.get_base_type('Module'), result.type)
        
    def test_simple_class(self):
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        mod.write('class SampleClass(object):\n    pass\n')
        mod_element = self.pycore.get_module('mod')
        result = mod_element.get_attributes()['SampleClass']
        self.assertEquals(PyObject.get_base_type('Type'), result.get_type())

    def test_simple_function(self):
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        mod.write('def sample_function():\n    pass\n')
        mod_element = self.pycore.get_module('mod')
        result = mod_element.get_attributes()['sample_function']
        self.assertEquals(PyObject.get_base_type('Function'), result.get_type())

    def test_class_methods(self):
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        mod.write('class SampleClass(object):\n    def sample_method(self):\n        pass\n')
        mod_element = self.pycore.get_module('mod')
        sample_class = mod_element.get_attributes()['SampleClass']
        self.assertEquals(1, len(sample_class.get_attributes()))
        method = sample_class.get_attributes()['sample_method']
        self.assertEquals(PyObject.get_base_type('Function'), method.get_type())

    def test_global_variables(self):
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        mod.write('var = 10')
        mod_element = self.pycore.get_module('mod')
        result = mod_element.get_attributes()['var']
        
    def test_class_variables(self):
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        mod.write('class SampleClass(object):\n    var = 10\n')
        mod_element = self.pycore.get_module('mod')
        sample_class = mod_element.get_attributes()['SampleClass']
        var = sample_class.get_attributes()['var']
        
    def test_class_attributes_set_in_init(self):
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        mod.write('class SampleClass(object):\n    def __init__(self):\n        self.var = 20\n')
        mod_element = self.pycore.get_module('mod')
        sample_class = mod_element.get_attributes()['SampleClass']
        var = sample_class.get_attributes()['var']
        
    def test_classes_inside_other_classes(self):
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        mod.write('class SampleClass(object):\n    class InnerClass(object):\n        pass\n\n')
        mod_element = self.pycore.get_module('mod')
        sample_class = mod_element.get_attributes()['SampleClass']
        var = sample_class.get_attributes()['InnerClass']
        self.assertEquals(PyObject.get_base_type('Type'), var.get_type())

    def test_non_existant_module(self):
        try:
            self.pycore.get_module('mod')
            self.fail('And exception should have been raised')
        except ModuleNotFoundException:
            pass

    def test_imported_names(self):
        self.pycore.create_module(self.project.get_root_folder(), 'mod1')
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod2')
        mod.write('import mod1\n')
        module = self.pycore.get_module('mod2')
        imported_sys = module.get_attributes()['mod1']
        self.assertEquals(PyObject.get_base_type('Module'), imported_sys.get_type())

    def test_importing_out_of_project_names(self):
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        mod.write('import sys\n')
        module = self.pycore.get_module('mod')
        imported_sys = module.get_attributes()['sys']
        self.assertEquals(PyObject.get_base_type('Module'), imported_sys.get_type())

    def test_imported_as_names(self):
        self.pycore.create_module(self.project.get_root_folder(), 'mod1')
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod2')
        mod.write('import mod1 as my_import\n')
        module = self.pycore.get_module('mod2')
        imported_mod = module.get_attributes()['my_import']
        self.assertEquals(PyObject.get_base_type('Module'), imported_mod.get_type())

    def test_get_string_module(self):
        mod = self.pycore.get_string_module('class Sample(object):\n    pass\n')
        sample_class = mod.get_attributes()['Sample']
        self.assertEquals(PyObject.get_base_type('Type'), sample_class.get_type())

    def test_parameter_info_for_functions(self):
        mod = self.pycore.get_string_module('def sample_function(param1, param2=10,' +
                                            ' *param3, **param4):\n    pass')
        sample_function = mod.get_attributes()['sample_function']
        self.assertEquals(['param1', 'param2', 'param3', 'param4'], sample_function.object.parameters)

    def test_not_found_module_is_package(self):
        mod = self.pycore.get_string_module('import doesnotexist\n')
        self.assertFalse(mod.get_attributes()['doesnotexist'].object.is_package)

    def test_mixing_scopes_and_objects_hierarchy(self):
        mod = self.pycore.get_string_module('var = 200\n')
        scope = mod.get_scope()
        self.assertTrue('var' in scope.get_names())
    
    def test_function_scopes(self):
        scope = self.pycore.get_string_scope('def func():    var = 10\n')
        func_scope = scope.get_scopes()[0]
        self.assertTrue('var' in func_scope.get_names())

    def test_function_scopes_classes(self):
        scope = self.pycore.get_string_scope('def func():\n    class Sample(object):\n        pass\n')
        func_scope = scope.get_scopes()[0]
        self.assertTrue('Sample' in func_scope.get_names())

    def test_function_getting_scope(self):
        mod = self.pycore.get_string_module('def func():    var = 10\n')
        func_scope = mod.get_attributes()['func'].object.get_scope()
        self.assertTrue('var' in func_scope.get_names())

    def test_scopes_in_function_scopes(self):
        scope = self.pycore.get_string_scope('def func():\n    def inner():\n        var = 10\n')
        func_scope = scope.get_scopes()[0]
        inner_scope = func_scope.get_scopes()[0]
        self.assertTrue('var' in inner_scope.get_names())

    def test_inheriting_base_class_attributes(self):
        mod = self.pycore.get_string_module('class Base(object):\n    def method(self):\n        pass\n' +
                                             'class Derived(Base):\n    pass\n')
        derived = mod.get_attributes()['Derived']
        self.assertTrue('method' in derived.get_attributes())
        self.assertEquals(PyObject.get_base_type('Function'), derived.get_attributes()['method'].get_type())

    def test_inheriting_multiple_base_class_attributes(self):
        mod = self.pycore.get_string_module('class Base1(object):\n    def method1(self):\n        pass\n' +
                                            'class Base2(object):\n    def method2(self):\n        pass\n' +
                                             'class Derived(Base1, Base2):\n    pass\n')
        derived = mod.get_attributes()['Derived']
        self.assertTrue('method1' in derived.get_attributes())
        self.assertTrue('method2' in derived.get_attributes())

    def test_inheriting_unknown_base_class(self):
        mod = self.pycore.get_string_module('class Derived(NotFound):\n    def f(self):\n        pass\n')
        derived = mod.get_attributes()['Derived']
        self.assertTrue('f' in derived.get_attributes())

    def test_module_creation(self):
        new_module = self.pycore.create_module(self.project.get_root_folder(), 'module')
        self.assertFalse(new_module.is_folder())
        self.assertEquals(self.project.get_resource('module.py'), new_module)

    def test_packaged_module_creation(self):
        package = self.project.get_root_folder().create_folder('package')
        new_module = self.pycore.create_module(self.project.get_root_folder(), 'package.module')
        self.assertEquals(self.project.get_resource('package/module.py'), new_module)

    def test_packaged_module_creation_with_nested_src(self):
        src = self.project.get_root_folder().create_folder('src')
        package = src.create_folder('pkg')
        new_module = self.pycore.create_module(src, 'pkg.mod')
        self.assertEquals(self.project.get_resource('src/pkg/mod.py'), new_module)

    def test_package_creation(self):
        new_package = self.pycore.create_package(self.project.get_root_folder(), 'pkg')
        self.assertTrue(new_package.is_folder())
        self.assertEquals(self.project.get_resource('pkg'), new_package)
        self.assertEquals(self.project.get_resource('pkg/__init__.py'), 
                          new_package.get_child('__init__.py'));

    def test_nested_package_creation(self):
        package = self.pycore.create_package(self.project.get_root_folder(), 'pkg1')
        nested_package = self.pycore.create_package(self.project.get_root_folder(), 'pkg1.pkg2')
        self.assertEquals(self.project.get_resource('pkg1/pkg2'), nested_package)

    def test_packaged_package_creation_with_nested_src(self):
        src = self.project.get_root_folder().create_folder('src')
        package = self.pycore.create_package(src, 'pkg1')
        nested_package = self.pycore.create_package(src, 'pkg1.pkg2')
        self.assertEquals(self.project.get_resource('src/pkg1/pkg2'), nested_package)

    def test_find_module(self):
        src = self.project.get_root_folder().create_folder('src')
        samplemod = self.pycore.create_module(src, 'samplemod')
        found_modules = self.pycore.find_module('samplemod')
        self.assertEquals(1, len(found_modules))
        self.assertEquals(samplemod, found_modules[0])

    def test_find_nested_module(self):
        src = self.project.get_root_folder().create_folder('src')
        samplepkg = self.pycore.create_package(src, 'samplepkg')
        samplemod = self.pycore.create_module(samplepkg, 'samplemod')
        found_modules = self.pycore.find_module('samplepkg.samplemod')
        self.assertEquals(1, len(found_modules))
        self.assertEquals(samplemod, found_modules[0])

    def test_find_multiple_module(self):
        src = self.project.get_root_folder().create_folder('src')
        samplemod1 = self.pycore.create_module(src, 'samplemod')
        samplemod2 = self.pycore.create_module(self.project.get_root_folder(), 'samplemod')
        test = self.project.get_root_folder().create_folder('test')
        samplemod3 = self.pycore.create_module(test, 'samplemod')
        found_modules = self.pycore.find_module('samplemod')
        self.assertEquals(3, len(found_modules))
        self.assertTrue(samplemod1 in found_modules and samplemod2 in found_modules and \
                        samplemod3 in found_modules)

    def test_find_module_packages(self):
        src = self.project.get_root_folder()
        samplepkg = self.pycore.create_package(src, 'samplepkg')
        found_modules = self.pycore.find_module('samplepkg')
        self.assertEquals(1, len(found_modules))
        self.assertEquals(samplepkg, found_modules[0])

    def test_find_module_when_module_and_package_with_the_same_name(self):
        src = self.project.get_root_folder()
        samplemod = self.pycore.create_module(src, 'sample')
        samplepkg = self.pycore.create_package(src, 'sample')
        found_modules = self.pycore.find_module('sample')
        self.assertEquals(1, len(found_modules))
        self.assertEquals(samplepkg, found_modules[0])

    def test_getting_empty_source_folders(self):
        self.assertEquals([], self.pycore.get_source_folders())

    def test_root_source_folder(self):
        self.project.get_root_folder().create_file('sample.py')
        source_folders = self.pycore.get_source_folders()
        self.assertEquals(1, len(source_folders))
        self.assertTrue(self.project.get_root_folder() in source_folders)

    def test_src_source_folder(self):
        src = self.project.get_root_folder().create_folder('src')
        src.create_file('sample.py')
        source_folders = self.pycore.get_source_folders()
        self.assertEquals(1, len(source_folders))
        self.assertTrue(self.project.get_resource('src') in source_folders)

    def test_packages(self):
        src = self.project.get_root_folder().create_folder('src')
        pkg = src.create_folder('package')
        pkg.create_file('__init__.py')
        source_folders = self.pycore.get_source_folders()
        self.assertEquals(1, len(source_folders))
        self.assertTrue(src in source_folders)

    def test_multi_source_folders(self):
        src = self.project.get_root_folder().create_folder('src')
        package = src.create_folder('package')
        package.create_file('__init__.py')
        test = self.project.get_root_folder().create_folder('test')
        test.create_file('alltests.py')
        source_folders = self.pycore.get_source_folders()
        self.assertEquals(2, len(source_folders))
        self.assertTrue(src in source_folders)
        self.assertTrue(test in source_folders)

    def test_multi_source_folders2(self):
        mod1 = self.pycore.create_module(self.project.get_root_folder(), 'mod1')
        src = self.project.get_root_folder().create_folder('src')
        package = self.pycore.create_package(src, 'package')
        mod2 = self.pycore.create_module(package, 'mod2')
        source_folders = self.pycore.get_source_folders()
        self.assertEquals(2, len(source_folders))
        self.assertTrue(self.project.get_root_folder() in source_folders and \
                        src in source_folders)

    def test_get_pyname_definition_location(self):
        mod = self.pycore.get_string_module('a_var = 20\n')
        a_var = mod.get_attributes()['a_var']
        self.assertEquals((None, 1), a_var.get_definition_location())

    def test_get_pyname_definition_location_functions(self):
        mod = self.pycore.get_string_module('def a_func():\n    pass\n')
        a_func = mod.get_attributes()['a_func']
        self.assertEquals((None, 1), a_func.get_definition_location())

    def test_get_pyname_definition_location_class(self):
        mod = self.pycore.get_string_module('class AClass(object):\n    pass\n\n')
        a_class = mod.get_attributes()['AClass']
        self.assertEquals((None, 1), a_class.get_definition_location())

    def test_get_pyname_definition_location_local_variables(self):
        mod = self.pycore.get_string_module('def a_func():\n    a_var = 10\n')
        a_func_scope = mod.get_scope().get_scopes()[0]
        a_var = a_func_scope.get_names()['a_var']
        self.assertEquals((None, 2), a_var.get_definition_location())

    def test_get_pyname_definition_location_reassigning(self):
        mod = self.pycore.get_string_module('a_var = 20\na_var=30\n')
        a_var = mod.get_attributes()['a_var']
        self.assertEquals((None, 1), a_var.get_definition_location())

    def test_get_pyname_definition_location_importes(self):
        module = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        mod = self.pycore.get_string_module('import mod\n')
        module_pyname = mod.get_attributes()['mod']
        self.assertEquals((module, 1), module_pyname.get_definition_location())

    def test_get_pyname_definition_location_imports(self):
        module_resource = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        module_resource.write('\ndef a_func():\n    pass\n')
        mod = self.pycore.get_string_module('from mod import a_func\n')
        a_func = mod.get_attributes()['a_func']
        self.assertEquals((module_resource, 2), a_func.get_definition_location())

    def test_get_pyname_definition_location_parameters(self):
        mod = self.pycore.get_string_module('def a_func(param1, param2):\n    a_var = param\n')
        a_func_scope = mod.get_scope().get_scopes()[0]
        param1 = a_func_scope.get_names()['param1']
        self.assertEquals((None, 1), param1.get_definition_location())
        param2 = a_func_scope.get_names()['param2']
        self.assertEquals((None, 1), param2.get_definition_location())

    def test_module_get_resource(self):
        module_resource = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        module = self.pycore.get_module('mod')
        self.assertEquals(module_resource, module.get_resource())
        string_module = self.pycore.get_string_module('from mod import a_func\n')
        self.assertEquals(None, string_module.get_resource())
        
    def test_get_pyname_definition_location_class(self):
        mod = self.pycore.get_string_module('class AClass(object):\n    def __init__(self):\n' + \
                                            '        self.an_attr = 10\n')
        a_class = mod.get_attributes()['AClass']
        an_attr = a_class.get_attributes()['an_attr']
        self.assertEquals((None, 3), an_attr.get_definition_location())

    def test_import_not_found_module_get_definition_location(self):
        mod = self.pycore.get_string_module('import doesnotexist\n')
        does_not_exist = mod.get_attributes()['doesnotexist']
        self.assertEquals((None, None), does_not_exist.get_definition_location())

    def test_from_not_found_module_get_definition_location(self):
        mod = self.pycore.get_string_module('from doesnotexist import Sample\n')
        sample = mod.get_attributes()['Sample']
        self.assertEquals((None, None), sample.get_definition_location())

    def test_from_package_import_module_get_definition_location(self):
        pkg = self.pycore.create_package(self.project.get_root_folder(), 'pkg')
        mod = self.pycore.create_module(pkg, 'mod')
        pymod = self.pycore.get_string_module('from pkg import mod\n')
        imported_module = pymod.get_attributes()['mod']
        self.assertEquals((mod, 1), imported_module.get_definition_location())

    def test_get_module_for_defined_pyobjects(self):
        mod = self.pycore.get_string_module('class AClass(object):\n    pass\n')
        a_class = mod.get_attributes()['AClass'].get_object()
        self.assertEquals(mod, a_class.get_module())
        
    def test_get_definition_location_for_packages(self):
        pkg = self.pycore.create_package(self.project.get_root_folder(), 'pkg')
        init_dot_py = pkg.get_child('__init__.py')
        mod = self.pycore.get_string_module('import pkg')
        pkg_pyname = mod.get_attributes()['pkg']
        self.assertEquals((init_dot_py, 1), pkg_pyname.get_definition_location())
        
    # TODO: Eliminate PyFilteredPackage
    def xxx_test_get_definition_location_for_filtered_packages(self):
        pkg = self.pycore.create_package(self.project.get_root_folder(), 'pkg')
        self.pycore.create_module(pkg, 'mod')
        init_dot_py = pkg.get_child('__init__.py')
        mod = self.pycore.get_string_module('import pkg.mod')
        pkg_pyname = mod.get_attributes()['pkg']
        self.assertEquals((init_dot_py, 1), pkg_pyname.get_definition_location())
        
    def test_simple_type_inferencing(self):
        scope = self.pycore.get_string_scope('class Sample(object):\n    pass\na_var = Sample()\n')
        sample_class = scope.get_names()['Sample'].get_object()
        a_var = scope.get_names()['a_var']
        self.assertEquals(sample_class, a_var.get_type())
        
    def test_simple_type_inferencing_classes_defined_in_holding_scope(self):
        scope = self.pycore.get_string_scope('class Sample(object):\n    pass\n' +
                                        'def a_func():\n    a_var = Sample()\n')
        sample_class = scope.get_names()['Sample'].get_object()
        a_var = scope.get_names()['a_func'].get_object().get_scope().get_names()['a_var']
        self.assertEquals(sample_class, a_var.get_type())
        
    def test_simple_type_inferencing_classes_in_class_methods(self):
        scope = self.pycore.get_string_scope('class Sample(object):\n    pass\n' +
                                             'class Another(object):\n' + 
                                             '    def a_method():\n        a_var = Sample()\n')
        sample_class = scope.get_names()['Sample'].get_object()
        another_class = scope.get_names()['Another']
        a_var = another_class.get_attributes()['a_method'].get_object().get_scope().get_names()['a_var']
        self.assertEquals(sample_class, a_var.get_type())
        
    def test_simple_type_inferencing_class_attributes(self):
        scope = self.pycore.get_string_scope('class Sample(object):\n    pass\n' +
                                             'class Another(object):\n' + 
                                             '    def __init__(self):\n        self.a_var = Sample()\n')
        sample_class = scope.get_names()['Sample'].get_object()
        another_class = scope.get_names()['Another']
        a_var = another_class.get_attributes()['a_var']
        self.assertEquals(sample_class, a_var.get_type())

    def test_simple_type_inferencing_for_in_class_assignments(self):
        scope = self.pycore.get_string_scope('class Sample(object):\n    pass\n' +
                                             'class Another(object):\n    an_attr = Sample()\n')
        sample_class = scope.get_names()['Sample'].get_object()
        another_class = scope.get_names()['Another'].get_object()
        an_attr = another_class.get_attributes()['an_attr']
        self.assertEquals(sample_class, an_attr.get_type())

    def test_out_of_project_modules(self):
        scope = self.pycore.get_string_scope('import rope.outline as outline\n')
        imported_module = scope.get_names()['outline']
        self.assertTrue('Outline' in imported_module.get_attributes())


class PyCoreInProjectsTest(unittest.TestCase):

    def setUp(self):
        super(self.__class__, self).setUp()
        self.project_root = 'sample_project'
        testutils.remove_recursively(self.project_root)
        os.mkdir(self.project_root)
        self.project = Project(self.project_root)
        self.pycore = self.project.get_pycore()
        samplemod = self.pycore.create_module(self.project.get_root_folder(), 'samplemod')
        samplemod.write("class SampleClass(object):\n    def sample_method():\n        pass" + \
                        "\n\ndef sample_func():\n    pass\nsample_var = 10\n" + \
                        "\ndef _underlined_func():\n    pass\n\n" )
        package = self.pycore.create_package(self.project.get_root_folder(), 'package')
        nestedmod = self.pycore.create_module(package, 'nestedmod')

    def tearDown(self):
        testutils.remove_recursively(self.project_root)
        super(self.__class__, self).tearDown()

    def test_simple_import(self):
        mod = self.pycore.get_string_module('import samplemod\n')
        samplemod = mod.get_attributes()['samplemod']
        self.assertEquals(PyObject.get_base_type('Module'), samplemod.get_type())

    def test_from_import_class(self):
        mod = self.pycore.get_string_module('from samplemod import SampleClass\n')
        result = mod.get_attributes()['SampleClass']
        self.assertEquals(PyObject.get_base_type('Type'), result.get_type())
        self.assertTrue('sample_func' not in mod.get_attributes())

    def test_from_import_star(self):
        mod = self.pycore.get_string_module('from samplemod import *\n')
        self.assertEquals(PyObject.get_base_type('Type'),
                          mod.get_attributes()['SampleClass'].get_type())
        self.assertEquals(PyObject.get_base_type('Function'),
                          mod.get_attributes()['sample_func'].get_type())
        self.assertTrue(mod.get_attributes()['sample_var'] is not None)

    def test_from_import_star_not_imporing_underlined(self):
        mod = self.pycore.get_string_module('from samplemod import *')
        self.assertTrue('_underlined_func' not in mod.get_attributes())

    def test_from_package_import_mod(self):
        mod = self.pycore.get_string_module('from package import nestedmod\n')
        self.assertEquals(PyObject.get_base_type('Module'),
                          mod.get_attributes()['nestedmod'].get_type())

    def test_from_package_import_star(self):
        mod = self.pycore.get_string_module('from package import *\nnest')
        self.assertTrue('nestedmod' not in mod.get_attributes())

    def test_unknown_when_module_cannot_be_found(self):
        mod = self.pycore.get_string_module('from doesnotexist import nestedmod\n')
        self.assertTrue('nestedmod' in mod.get_attributes())

    def test_from_import_function(self):
        scope = self.pycore.get_string_scope('def f():\n    from samplemod import SampleClass\n')
        self.assertEquals(PyObject.get_base_type('Type'), 
                          scope.get_scopes()[0].get_names()['SampleClass'].get_type())

    def test_circular_imports(self):
        mod1 = self.pycore.create_module(self.project.get_root_folder(), 'mod1')
        mod2 = self.pycore.create_module(self.project.get_root_folder(), 'mod2')
        mod1.write('import mod2\n')
        mod2.write('import mod1\n')
        module1 = self.pycore.get_module('mod1')

    def test_circular_imports2(self):
        mod1 = self.pycore.create_module(self.project.get_root_folder(), 'mod1')
        mod2 = self.pycore.create_module(self.project.get_root_folder(), 'mod2')
        mod1.write('from mod2 import Sample2\nclass Sample1(object):\n    pass\n')
        mod2.write('from mod1 import Sample1\nclass Sample2(object):\n    pass\n')
        module1 = self.pycore.get_module('mod1').get_attributes()

    def test_multi_dot_imports(self):
        pkg = self.pycore.create_package(self.project.get_root_folder(), 'pkg')
        pkg_mod = self.pycore.create_module(pkg, 'mod')
        pkg_mod.write('def sample_func():\n    pass\n')
        mod = self.pycore.get_string_module('import pkg.mod\n')
        self.assertTrue('pkg' in mod.get_attributes())
        self.assertTrue('sample_func' in 
                        mod.get_attributes()['pkg'].get_attributes()['mod'].get_attributes())
        
    def test_multi_dot_imports2(self):
        pkg = self.pycore.create_package(self.project.get_root_folder(), 'pkg')
        mod1 = self.pycore.create_module(pkg, 'mod1')
        mod2 = self.pycore.create_module(pkg, 'mod2')
        mod = self.pycore.get_string_module('import pkg.mod1\nimport pkg.mod2\n')
        package = mod.get_attributes()['pkg']
        self.assertEquals(2, len(package.get_attributes()))
        self.assertTrue('mod1' in package.get_attributes() and
                        'mod2' in package.get_attributes())
        
    def test_multi_dot_imports3(self):
        pkg1 = self.pycore.create_package(self.project.get_root_folder(), 'pkg1')
        pkg2 = self.pycore.create_package(pkg1, 'pkg2')
        mod1 = self.pycore.create_module(pkg2, 'mod1')
        mod2 = self.pycore.create_module(pkg2, 'mod2')
        mod = self.pycore.get_string_module('import pkg1.pkg2.mod1\nimport pkg1.pkg2.mod2\n')
        package1 = mod.get_attributes()['pkg1']
        package2 = package1.get_attributes()['pkg2']
        self.assertEquals(2, len(package2.get_attributes()))
        self.assertTrue('mod1' in package2.get_attributes() and
                        'mod2' in package2.get_attributes())
        
    def test_multi_dot_imports_as(self):
        pkg = self.pycore.create_package(self.project.get_root_folder(), 'pkg')
        mod1 = self.pycore.create_module(pkg, 'mod1')
        mod1.write('def f():\n    pass\n')
        mod = self.pycore.get_string_module('import pkg.mod1 as mod1\n')
        module = mod.get_attributes()['mod1']
        self.assertTrue('f' in module.get_attributes())
        
    def test_from_package_import_package(self):
        pkg1 = self.pycore.create_package(self.project.get_root_folder(), 'pkg1')
        pkg2 = self.pycore.create_package(pkg1, 'pkg2')
        module = self.pycore.create_module(pkg2, 'mod')
        mod = self.pycore.get_string_module('from pkg1 import pkg2\n')
        package = mod.get_attributes()['pkg2']
        self.assertEquals(0, len(package.get_attributes()))

    def test_invalidating_cache_after_resource_change(self):
        module = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        module.write('import sys\n')
        mod1 = self.pycore.get_module('mod')
        self.assertTrue('var' not in mod1.get_attributes())
        module.write('var = 10\n')
        mod2 = self.pycore.get_module('mod')
        self.assertTrue('var' in mod2.get_attributes())

    def test_from_import_nonexistant_module(self):
        mod = self.pycore.get_string_module('from doesnotexistmod import DoesNotExistClass\n')
        self.assertTrue('DoesNotExistClass' in mod.get_attributes())
        self.assertEquals(PyObject.get_base_type('Unknown'),
                          mod.get_attributes()['DoesNotExistClass'].get_type())

    def test_from_import_nonexistant_name(self):
        mod = self.pycore.get_string_module('from samplemod import DoesNotExistClass\n')
        self.assertTrue('DoesNotExistClass' in mod.get_attributes())
        self.assertEquals(PyObject.get_base_type('Unknown'),
                          mod.get_attributes()['DoesNotExistClass'].get_type())

    def test_not_considering_imported_names_as_sub_scopes(self):
        scope = self.pycore.get_string_scope('from samplemod import SampleClass\n')
        self.assertEquals(0, len(scope.get_scopes()))

    def test_not_considering_imported_modules_as_sub_scopes(self):
        scope = self.pycore.get_string_scope('import samplemod\n')
        self.assertEquals(0, len(scope.get_scopes()))

    def test_inheriting_dotted_base_class(self):
        mod = self.pycore.get_string_module('import samplemod\n' + 
                                            'class Derived(samplemod.SampleClass):\n    pass\n')
        derived = mod.get_attributes()['Derived']
        self.assertTrue('sample_method' in derived.get_attributes())

    def test_self_in_methods(self):
        scope = self.pycore.get_string_scope('class Sample(object):\n    def func(self):\n        pass\n')
        sample_class = scope.get_names()['Sample'].object
        func_scope = scope.get_scopes()[0].get_scopes()[0]
        self.assertEquals(sample_class, func_scope.get_names()['self'].get_type())
        self.assertTrue('func' in func_scope.get_names()['self'].get_attributes())

    def test_self_in_methods_with_decorators(self):
        scope = self.pycore.get_string_scope('class Sample(object):\n    @staticmethod\n' +
                                             '    def func(self):\n        pass\n')
        sample_class = scope.get_names()['Sample'].object
        func_scope = scope.get_scopes()[0].get_scopes()[0]
        self.assertNotEquals(sample_class, func_scope.get_names()['self'].get_type())

    def test_location_of_imports_when_importing(self):
        mod = self.pycore.create_module(self.project.get_root_folder(), 'mod')
        mod.write('from samplemod import SampleClass\n')
        scope = self.pycore.get_string_scope('from mod import SampleClass\n')
        sample_class = scope.get_names()['SampleClass']
        samplemod = self.pycore.get_module('samplemod').get_resource()
        self.assertEquals((samplemod, 1), sample_class.get_definition_location())
        

class PyCoreScopesTest(unittest.TestCase):

    def setUp(self):
        super(PyCoreScopesTest, self).setUp()
        self.project_root = 'sample_project'
        testutils.remove_recursively(self.project_root)
        self.project = Project(self.project_root)
        self.pycore = self.project.get_pycore()

    def tearDown(self):
        testutils.remove_recursively(self.project_root)
        super(PyCoreScopesTest, self).tearDown()

    def test_simple_scope(self):
        scope = self.pycore.get_string_scope('def sample_func():\n    pass\n')
        sample_func = scope.get_names()['sample_func']
        self.assertEquals(PyObject.get_base_type('Function'), sample_func.get_type())

    def test_simple_function_scope(self):
        scope = self.pycore.get_string_scope('def sample_func():\n    a = 10\n')
        self.assertEquals(1, len(scope.get_scopes()))
        sample_func_scope = scope.get_scopes()[0]
        self.assertEquals(1, len(sample_func_scope.get_names()))
        self.assertEquals(0, len(sample_func_scope.get_scopes()))

    def test_classes_inside_function_scopes(self):
        scope = self.pycore.get_string_scope('def sample_func():\n' +
                                             '    class SampleClass(object):\n        pass\n')
        self.assertEquals(1, len(scope.get_scopes()))
        sample_func_scope = scope.get_scopes()[0]
        self.assertEquals(PyObject.get_base_type('Type'), 
                          scope.get_scopes()[0].get_names()['SampleClass'].get_type())

    def test_simple_class_scope(self):
        scope = self.pycore.get_string_scope('class SampleClass(object):\n' +
                                             '    def f(self):\n        var = 10\n')
        self.assertEquals(1, len(scope.get_scopes()))
        sample_class_scope = scope.get_scopes()[0]
        self.assertEquals(0, len(sample_class_scope.get_names()))
        self.assertEquals(1, len(sample_class_scope.get_scopes()))
        f_in_class = sample_class_scope.get_scopes()[0]
        self.assertTrue('var' in f_in_class.get_names())

    def test_get_lineno(self):
        scope = self.pycore.get_string_scope('\ndef sample_func():\n    a = 10\n')
        self.assertEquals(1, len(scope.get_scopes()))
        sample_func_scope = scope.get_scopes()[0]
        self.assertEquals(1, scope.get_lineno())
        self.assertEquals(2, sample_func_scope.get_lineno())

    def test_scope_kind(self):
        scope = self.pycore.get_string_scope('class SampleClass(object):\n    pass\n' +
                                             'def sample_func():\n    pass\n')
        sample_class_scope = scope.get_scopes()[0]
        sample_func_scope = scope.get_scopes()[1]
        self.assertEquals('Module', scope.get_kind())
        self.assertEquals('Class', sample_class_scope.get_kind())
        self.assertEquals('Function', sample_func_scope.get_kind())

    def test_function_parameters_in_scope_names(self):
        scope = self.pycore.get_string_scope('def sample_func(param):\n    a = 10\n')
        sample_func_scope = scope.get_scopes()[0]
        self.assertTrue('param' in sample_func_scope.get_names())

    def test_get_names_contains_only_names_defined_in_a_scope(self):
        scope = self.pycore.get_string_scope('var1 = 10\ndef sample_func(param):\n    var2 = 20\n')
        sample_func_scope = scope.get_scopes()[0]
        self.assertTrue('var1' not in sample_func_scope.get_names())

    def test_scope_lookup(self):
        scope = self.pycore.get_string_scope('var1 = 10\ndef sample_func(param):\n    var2 = 20\n')
        self.assertTrue(scope.lookup('var2') is None)
        self.assertEquals(PyObject.get_base_type('Function'), scope.lookup('sample_func').get_type())
        sample_func_scope = scope.get_scopes()[0]
        self.assertTrue(sample_func_scope.lookup('var1') is not None)


class PythonFileRunnerTest(unittest.TestCase):

    def setUp(self):
        super(PythonFileRunnerTest, self).setUp()
        self.project_root = 'sample_project'
        testutils.remove_recursively(self.project_root)
        self.project = Project(self.project_root)
        self.pycore = self.project.get_pycore()

    def tearDown(self):
        testutils.remove_recursively(self.project_root)
        super(PythonFileRunnerTest, self).tearDown()

    def make_sample_python_file(self, file_path, get_text_function_source=None):
        self.project.get_root_folder().create_file(file_path)
        file = self.project.get_resource(file_path)
        if not get_text_function_source:
            get_text_function_source = "def get_text():\n    return 'run'\n\n"
        file_content = get_text_function_source + \
                       "output = open('output.txt', 'w')\noutput.write(get_text())\noutput.close()\n"
        file.write(file_content)
        
    def get_output_file_content(self, file_path):
        try:
            output_path = ''
            last_slash = file_path.rfind('/')
            if last_slash != -1:
                output_path = file_path[0:last_slash + 1]
            file = self.project.get_resource(output_path + 'output.txt')
            return file.read()
        except RopeException:
            return ''

    def test_making_runner(self):
        file_path = 'sample.py'
        self.make_sample_python_file(file_path)
        file_resource = self.project.get_resource(file_path)
        runner = PythonFileRunner(file_resource)
        runner.wait_process()
        self.assertEquals('run', self.get_output_file_content(file_path))

    # FIXME: this does not work on windows
    def xxx_test_killing_runner(self):
        file_path = 'sample.py'
        self.make_sample_python_file(file_path,
                                     "def get_text():" +
                                     "\n    import time\n    time.sleep(1)\n    return 'run'\n")
        file_resource = self.project.get_resource(file_path)
        runner = PythonFileRunner(file_resource)
        runner.kill_process()
        self.assertEquals('', self.get_output_file_content(file_path))

    def test_running_nested_files(self):
        self.project.get_root_folder().create_folder('src')
        file_path = 'src/sample.py'
        self.make_sample_python_file(file_path)
        file_resource = self.project.get_resource(file_path)
        runner = PythonFileRunner(file_resource)
        runner.wait_process()
        self.assertEquals('run', self.get_output_file_content(file_path))

    def test_setting_process_input(self):
        file_path = 'sample.py'
        self.make_sample_python_file(file_path,
                                     "def get_text():" +
                                     "\n    import sys\n    return sys.stdin.readline()\n")
        temp_file_name = 'processtest.tmp'
        try:
            temp_file = open(temp_file_name, 'w')
            temp_file.write('input text\n')
            temp_file.close()
            file_resource = self.project.get_resource(file_path)
            stdin = open(temp_file_name)
            runner = PythonFileRunner(file_resource, stdin=stdin)
            runner.wait_process()
            stdin.close()
            self.assertEquals('input text\n', self.get_output_file_content(file_path))
        finally:
            os.remove(temp_file_name)
        
    def test_setting_process_output(self):
        file_path = 'sample.py'
        self.make_sample_python_file(file_path,
                                     "def get_text():" +
                                     "\n    print 'output text'\n    return 'run'\n")
        temp_file_name = 'processtest.tmp'
        try:
            file_resource = self.project.get_resource(file_path)
            stdout = open(temp_file_name, 'w')
            runner = PythonFileRunner(file_resource, stdout=stdout)
            runner.wait_process()
            stdout.close()
            temp_file = open(temp_file_name, 'r')
            self.assertEquals('output text\n', temp_file.read())
            temp_file.close()
        finally:
            os.remove(temp_file_name)

    def test_setting_pythonpath(self):
        src = self.project.get_root_folder().create_folder('src')
        src.create_file('sample.py')
        src.get_child('sample.py').write('def f():\n    pass\n')
        self.project.get_root_folder().create_folder('test')
        file_path = 'test/test.py'
        self.make_sample_python_file(file_path,
                                     "def get_text():" +
                                     "\n    import sample\n    sample.f()\n    return'run'\n")
        file_resource = self.project.get_resource(file_path)
        runner = PythonFileRunner(file_resource)
        runner.wait_process()
        self.assertEquals('run', self.get_output_file_content(file_path))

def suite():
    result = unittest.TestSuite()
    result.addTests(unittest.makeSuite(PyCoreTest))
    result.addTests(unittest.makeSuite(PyCoreInProjectsTest))
    result.addTests(unittest.makeSuite(PyCoreScopesTest))
    result.addTests(unittest.makeSuite(PythonFileRunnerTest))
    return result

if __name__ == '__main__':
    unittest.main()

