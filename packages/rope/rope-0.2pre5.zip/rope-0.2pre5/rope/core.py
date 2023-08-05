import tkMessageBox
import tkFileDialog
import tkSimpleDialog
from threading import Thread
from Tkinter import *

import rope.editor
import rope.fileeditor
import rope.statusbar
from rope.exceptions import RopeException
from rope.project import Project, FileFinder
from rope.pycore import PythonFileRunner


class EditorManager(object):

    def __init__(self, editor_panel, core):
        self.core = core
        self.editor_list = Frame(editor_panel, borderwidth=0)
        self.editor_frame = Frame(editor_panel, borderwidth=0, relief=RIDGE)
        self.editor_list.pack(fill=BOTH, side=TOP)
        self.editor_frame.pack(fill=BOTH, expand=1)
        self.editor_frame.pack_propagate(0)
        self.editors = []
        self.buttons = {}
        self.active_file_path = StringVar('')
        self.active_editor = None

    def activate_editor(self, editor):
        if self.active_editor:
            self.active_editor.get_editor().getWidget().forget()
        editor.get_editor().getWidget().pack(fill=BOTH, expand=1)
        editor.get_editor().getWidget().focus_set()
        self.buttons[editor].select()
        self.active_editor = editor
        self.editors.remove(editor)
        self.editors.insert(0, editor)

    def get_resource_editor(self, file_):
        for editor in self.editors:
            if editor.get_file() == file_:
                self.buttons[editor].invoke()
                return editor
        editor = rope.fileeditor.FileEditor(Core.get_core().get_open_project(), file_,
                                            rope.editor.GraphicalEditorFactory(self.editor_frame))
        editor.get_editor().set_status_bar_manager(self.core.status_bar_manager)
        self.editors.append(editor)
        title = Radiobutton(self.editor_list, text=file_.get_name(),
                            variable=self.active_file_path,
                            value=file_.get_path(), indicatoron=0, bd=2,
                            command=lambda: self.activate_editor(editor),
                            selectcolor='#99A', relief=GROOVE)
        self.buttons[editor] = title
        title.select()
        title.pack(fill=BOTH, side=LEFT)
        self.activate_editor(editor)
        self.core._set_key_binding(editor.get_editor().getWidget())
        return editor

    def switch_active_editor(self):
        if len(self.editors) >= 2:
            self.activate_editor(self.editors[1])

    def close_active_editor(self):
        if self.active_editor is None:
            return
        self.active_editor.get_editor().getWidget().forget()
        self.editors.remove(self.active_editor)
        self.buttons[self.active_editor].forget()
        del self.buttons[self.active_editor]
        self.active_editor = None
        if self.editors:
            self.buttons[self.editors[0]].invoke()

class Core(object):
    """The Core of the IDE"""

    def __init__(self):
        self.root = Tk()
        self.root.title('Rope')
        self.menubar = Menu(self.root, relief=RAISED, borderwidth=1)
        self.root['menu'] = self.menubar
        self._create_menu()

        self.main = Frame(self.root, height='13c', width='26c', relief=RIDGE, bd=2)
        self.editor_panel = Frame(self.main, borderwidth=0)
        self.editor_manager = EditorManager(self.editor_panel, self)

        self.status_bar = Frame(self.main, borderwidth=1, relief=RIDGE)
        self.status_bar_manager = rope.statusbar.StatusBarManager(self.status_bar)
        line_status = self.status_bar_manager.create_status('line')
        line_status.set_width(12)

        self._set_key_binding(self.root)
        self.root.protocol('WM_DELETE_WINDOW', self.exit)
        self.runningThread = Thread(target=self.run)
        self.project = None

    def _create_menu(self):
        fileMenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=fileMenu, underline=1)
        fileMenu.add_command(label='Open Project ...',
                             command=self._open_project_dialog, underline=6)
        fileMenu.add_command(label='Close Project',
                             command=self.close_project, underline=3)
        fileMenu.add_separator()
        fileMenu.add_command(label='New File ...',
                             command=self._create_new_file_dialog, underline=0)
        fileMenu.add_command(label='New Folder ...',
                             command=self._create_new_folder_dialog, underline=1)
        fileMenu.add_command(label='New Module ...',
                             command=self._create_module_dialog, underline=4)
        fileMenu.add_command(label='New Package ...',
                             command=self._create_package_dialog, underline=4)
        fileMenu.add_separator()
        fileMenu.add_command(label='Find File ...',
                             command=self._find_file_dialog, underline=0)
        fileMenu.add_command(label='Open File ...',
                             command=self._open_file_dialog, underline=0)
        fileMenu.add_separator()
        fileMenu.add_command(label='Exit',
                             command=self.exit, underline=1)

    def _set_key_binding(self, widget):
        widget.bind('<Control-x><Control-n>', self._create_new_file_dialog)
        def _save_active_editor(event):
            self.save_file()
            return 'break'
        widget.bind('<Control-x><Control-s>', _save_active_editor)
        widget.bind('<Control-x><Control-p>', self._open_project_dialog)
        def _exit(event):
            self.exit()
            return 'break'
        widget.bind('<Control-x><Control-c>', _exit)
        widget.bind('<Control-x><Control-d>', self._create_new_folder_dialog)
        widget.bind('<Control-R>', self._find_file_dialog)
        widget.bind('<Control-x><Control-f>', self._find_file_dialog)
        widget.bind('<Control-F11>', self._run_active_editor)
        def _close_active_editor(event):
            self.close_active_editor()
            return 'break'
        widget.bind('<Control-x><k>', _close_active_editor)
        widget.bind('<Control-x><b>', self._change_editor_dialog)
        def do_switch_active_editor(event):
            self.switch_active_editor()
            return 'break'
        widget.bind('<Control-KeyRelease-F6>', do_switch_active_editor)
        line_status = self.status_bar_manager.get_status('line')
        def show_current_line_number(event):
            line_text = ' '
            if self.editor_manager.active_editor:
                line_text = 'line : %d' % \
                              self.editor_manager.active_editor.get_editor().get_current_line_number()
            line_status.set_text(line_text)
        widget.bind('<Any-KeyRelease>', show_current_line_number, '+')
        widget.bind('<Any-Button>', show_current_line_number)
        widget.bind('<FocusIn>', show_current_line_number)

    def _find_file_dialog(self, event=None):
        if not self.project:
            tkMessageBox.showerror(parent=self.root, title='No Open Project',
                                   message='No project is open')
            return
        toplevel = Toplevel()
        toplevel.title('Find Project File')
        find_dialog = Frame(toplevel)
        name_label = Label(find_dialog, text='Name')
        name = Entry(find_dialog)
        found_label = Label(find_dialog, text='Matching Files')
        found = Listbox(find_dialog, selectmode=SINGLE, width=48, height=15)
        scrollbar = Scrollbar(find_dialog, orient=VERTICAL)
        scrollbar['command'] = found.yview
        found.config(yscrollcommand=scrollbar.set)
        file_finder = FileFinder(self.project)
        def name_changed(event):
            if name.get() == '':
                result = ()
            else:
                result = file_finder.find_files_starting_with(name.get())
            found.delete(0, END)
            for file_ in result:
                found.insert(END, file_.get_path())
            if result:
                found.selection_set(0)
        def open_selected():
            selection = found.curselection()
            if selection:
                resource_name = found.get(selection[0])
                self.open_file(resource_name)
                toplevel.destroy()
        def cancel():
            toplevel.destroy()
        name.bind('<Any-KeyRelease>', name_changed)
        name.bind('<Return>', lambda event: open_selected())
        name.bind('<Escape>', lambda event: cancel())
        found.bind('<Return>', lambda event: open_selected())
        found.bind('<Escape>', lambda event: cancel())
        def select_prev(event):
            active = found.index(ACTIVE)
            if active - 1 >= 0:
                found.activate(active - 1)
                found.see(active - 1)
        found.bind('<Control-p>', select_prev)
        def select_next(event):
            active = found.index(ACTIVE)
            if active + 1 < found.size():
                found.activate(active + 1)
                found.see(active + 1)
        found.bind('<Control-n>', select_next)
        name_label.grid(row=0, column=0, columnspan=2)
        name.grid(row=1, column=0, columnspan=2)
        found_label.grid(row=2, column=0, columnspan=2)
        found.grid(row=3, column=0, columnspan=1)
        scrollbar.grid(row=3, column=1, columnspan=1, sticky=N+S)
        find_dialog.grid()
        name.focus_set()
        toplevel.grab_set()
        self.root.wait_window(toplevel)
        if event:
            return 'break'

    def _change_editor_dialog(self, event=None):
        if not self.project:
            tkMessageBox.showerror(parent=self.root, title='No Open Project',
                                   message='No project is open')
            return
        toplevel = Toplevel()
        toplevel.title('Change Editor')
        find_dialog = Frame(toplevel)
        name_label = Label(find_dialog, text='Name')
        name = Entry(find_dialog)
        found_label = Label(find_dialog, text='Editors')
        found = Listbox(find_dialog, selectmode=SINGLE, width=28, height=9)
        scrollbar = Scrollbar(find_dialog, orient=VERTICAL)
        scrollbar['command'] = found.yview
        found.config(yscrollcommand=scrollbar.set)
        for editor in self.editor_manager.editors:
            found.insert(END, editor.get_file().get_name())
        if len(self.editor_manager.editors) >= 2:
            found.selection_set(1)
        def name_changed(event):
            if name.get() == '':
                return
            found.select_clear(0, END)
            found_index = -1
            for index, editor in enumerate(self.editor_manager.editors):
                if editor.get_file().get_name().startswith(name.get()):
                    found_index = index
                    break
            if found_index != -1:
                found.selection_set(found_index)
        def open_selected():
            selection = found.curselection()
            if selection:
                editor = self.editor_manager.editors[int(selection[0])]
                self.activate_editor(editor)
                toplevel.destroy()
        def cancel():
            toplevel.destroy()
        name.bind('<Any-KeyRelease>', name_changed)
        name.bind('<Return>', lambda event: open_selected())
        name.bind('<Escape>', lambda event: cancel())
        found.bind('<Return>', lambda event: open_selected())
        found.bind('<Escape>', lambda event: cancel())
        def select_prev(event):
            active = found.index(ACTIVE)
            if active - 1 >= 0:
                found.activate(active - 1)
                found.see(active - 1)
        found.bind('<Control-p>', select_prev)
        def select_next(event):
            active = found.index(ACTIVE)
            if active + 1 < found.size():
                found.activate(active + 1)
                found.see(active + 1)
        found.bind('<Control-n>', select_next)
        name_label.grid(row=0, column=0, columnspan=2)
        name.grid(row=1, column=0, columnspan=2)
        found_label.grid(row=2, column=0, columnspan=2)
        found.grid(row=3, column=0, columnspan=1)
        scrollbar.grid(row=3, column=1, columnspan=1, sticky=N+S)
        find_dialog.grid()
        name.focus_set()
        toplevel.grab_set()
        self.root.wait_window(toplevel)
        if event:
            return 'break'

    def _create_resource_dialog(self, creation_callback,
                                resource_name='File', parent_name='Parent Folder'):
        '''Ask user about the parent folder and the name of the resource to be created
        
        creation_callback is a function accepting the parent and the name
        '''
        if not self.project:
            tkMessageBox.showerror(parent=self.root, title='No Open Project',
                                   message='No project is open')
            return
        toplevel = Toplevel()
        toplevel.title('New ' + resource_name)
        create_dialog = Frame(toplevel)
        parent_label = Label(create_dialog, text=parent_name)
        parent_entry = Entry(create_dialog)
        resource_label = Label(create_dialog, text=('New ' + resource_name))
        resource_entry = Entry(create_dialog)
        
        def do_create_resource():
            parent_folder = self.project.get_resource(parent_entry.get())
            creation_callback(parent_folder, resource_entry.get())
            toplevel.destroy()
        def cancel():
            toplevel.destroy()
        parent_entry.bind('<Return>', lambda event: do_create_resource())
        parent_entry.bind('<Escape>', lambda event: cancel())
        resource_entry.bind('<Return>', lambda event: do_create_resource())
        resource_entry.bind('<Escape>', lambda event: cancel())
        parent_label.grid(row=0, column=0, sticky=W)
        parent_entry.grid(row=0, column=1)
        resource_label.grid(row=1, column=0, sticky=W)
        resource_entry.grid(row=1, column=1)
        create_dialog.grid()
        resource_entry.focus_set()
        toplevel.grab_set()
        self.root.wait_window(toplevel)

    def _create_module_dialog(self, event=None):
        def do_create_module(source_folder, module_name):
            new_module = self.project.get_pycore().create_module(source_folder,
                                                                 module_name)
            self.editor_manager.get_resource_editor(new_module)
        self._create_resource_dialog(do_create_module, 'Module', 'Source Folder')
        if event:
            return 'break'

    def _create_package_dialog(self, event=None):
        def do_create_package(source_folder, package_name):
            new_package = self.project.get_pycore().create_package(source_folder,
                                                                   package_name)
            self.editor_manager.get_resource_editor(new_package.get_child('__init__.py'))
        self._create_resource_dialog(do_create_package, 'Package', 'Source Folder')
        if event:
            return 'break'

    def _run_active_editor(self, event=None):
        if not self.editor_manager.active_editor:
            tkMessageBox.showerror(parent=self.root, title='No Open Editor',
                                   message='No Editor is open.')
            return
        self.run_active_editor()
        return 'break'

    def _open_file_dialog(self, event=None):
        if not self.project:
            tkMessageBox.showerror(parent=self.root, title='No Open Project',
                                   message='No project is open')
            return 'break'
        def doOpen(fileName):
                self.open_file(fileName)
        self._show_open_dialog(doOpen, 'Open File Dialog')
        return 'break'

    def _create_new_file_dialog(self, event=None):
        def do_create_file(parent_folder, file_name):
            new_file = parent_folder.create_file(file_name)
            self.editor_manager.get_resource_editor(new_file)
        self._create_resource_dialog(do_create_file, 'File', 'Parent Folder')
        if event:
            return 'break'

    def _create_new_folder_dialog(self, event=None):
        def do_create_folder(parent_folder, folder_name):
            new_folder = parent_folder.create_folder(folder_name)
        self._create_resource_dialog(do_create_folder, 'Folder', 'Parent Folder')
        if event:
            return 'break'

    def _open_project_dialog(self, event=None):
        def doOpen(projectRoot):
            self.open_project(projectRoot)
        directory = tkFileDialog.askdirectory(parent=self.root, title='Open Project')
        if directory:
            doOpen(directory)
        return 'break'

    def _show_open_dialog(self, openCommand, title='Open Dialog'):
        input_ = tkSimpleDialog.askstring(title, 'Address :', parent=self.root)
        if input_:
            try:
                openCommand(input_)
            except Exception, e:
                tkMessageBox.showerror(parent=self.root, title='Failed',
                                       message=str(e))

    def start(self):
        self.runningThread.start()

    def run(self):
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.main.rowconfigure(0, weight=1)
        self.main.columnconfigure(0, weight=1)
        self.editor_panel.pack(fill=BOTH, expand=1)
        self.status_bar.pack(fill=BOTH, side=BOTTOM)
        self.main.pack(fill=BOTH, expand=1)
        self.main.pack_propagate(0)
        self.root.mainloop()

    def open_file(self, fileName):
        if self.project is None:
            raise RopeException('No project is open')
        file_ = self.project.get_resource(fileName)
        return self.editor_manager.get_resource_editor(file_)

    def activate_editor(self, editor):
        self.editor_manager.activate_editor(editor)

    def close_active_editor(self):
        self.editor_manager.close_active_editor()

    def save_file(self):
        activeEditor = self.editor_manager.active_editor
        if activeEditor:
            activeEditor.save()

    def create_file(self, file_name):
        if self.project is None:
            raise RopeException('No project is open')
        try:
            last_slash = file_name.rindex('/')
            parent = project.get_resource(file_name[: last_slash])
            file_name = file_name[last_slash + 1:]
        except ValueError:
            parent = self.project.get_root_folder()
        parent.create_file(file_name)
        return self.open_file(file_name)

    def open_project(self, projectRoot):
        if self.project:
            self.close_project()
        self.project = Project(projectRoot)

    def close_project(self):
        while self.editor_manager.active_editor is not None:
            self.close_active_editor()
        self.project = None

    def create_folder(self, folder_name):
        try:
            last_slash = folder_name.rindex('/')
            parent = project.get_resource(folder_name[:last_slash])
            folder_name = folder_name[last_slash + 1:]
        except ValueError:
            parent = self.project.get_root_folder()
        parent.create_folder(folder_name)

    def exit(self):
        self.root.quit()

    def get_open_project(self):
        return self.project

    def run_active_editor(self):
        activeEditor = self.editor_manager.active_editor
        if activeEditor:
            runner = PythonFileRunner(activeEditor.get_file())
            return runner

    def switch_active_editor(self):
        self.editor_manager.switch_active_editor()

    def get_active_editor(self):
        return self.editor_manager.active_editor

    def get_editor_manager(self):
        return self.editor_manager

    @staticmethod
    def get_core():
        '''Get the singleton instance of Core'''
        if not hasattr(Core, '_core'):
            Core._core = Core()
        return Core._core

