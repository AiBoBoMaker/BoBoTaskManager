import tkinter as tk
import customtkinter as ctk
import json
from datetime import datetime

class CustomMenu(ctk.CTkFrame):
    def __init__(self, master, text, commands, colors, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.master = master  # 保存主窗口引用
        self.colors = colors
        self.commands = commands
        self.dropdown = None
        
        # 创建菜单按钮
        self.menu_button = ctk.CTkButton(
            self,
            text=text,
            font=("微软雅黑", 11),
            fg_color="transparent",
            text_color=colors["text"],
            hover_color=colors["hover"],
            height=25,
            width=60,
            command=self.show_dropdown
        )
        self.menu_button.pack(fill="x")
        
    def show_dropdown(self):
        # 如果有其他打开的菜单，先关闭它们
        for widget in self.master.winfo_children():
            if isinstance(widget, CustomMenu) and widget != self:
                if widget.dropdown is not None:
                    widget.hide_dropdown()
        
        if self.dropdown is None:
            # 获取菜单按钮位置
            x = self.winfo_rootx()
            y = self.winfo_rooty() + self.winfo_height()
            
            # 创建下拉菜单窗口
            self.dropdown = tk.Toplevel()
            self.dropdown.withdraw()  # 先隐藏窗口
            self.dropdown.overrideredirect(True)
            
            # 设置 Toplevel 窗口的背景色
            self.dropdown.configure(bg=self.colors["sidebar"])  # 设置外层背景色
            
            # 创建下拉菜单框架
            menu_frame = ctk.CTkFrame(
                self.dropdown,
                fg_color=self.colors["sidebar"],
                border_width=1,
                border_color=self.colors["border"]
            )
            menu_frame.pack(fill="both", expand=True, padx=0, pady=0)
            
            # 添加菜单项
            for label, command in self.commands.items():
                if label == "-":  # 分隔线
                    separator = ctk.CTkFrame(
                        menu_frame,
                        height=1,
                        fg_color=self.colors["border"]
                    )
                    separator.pack(fill="x", padx=5, pady=2)
                else:
                    btn = ctk.CTkButton(
                        menu_frame,
                        text=label,
                        font=("微软雅黑", 11),
                        fg_color="transparent",
                        text_color=self.colors["text"],
                        hover_color=self.colors["hover"],
                        anchor="w",
                        height=30,
                        command=lambda c=command: self.execute_command(c)
                    )
                    btn.pack(fill="x", padx=1, pady=1)
            
            # 设置窗口位置并显示
            self.dropdown.geometry(f"+{x}+{y}")
            self.dropdown.update_idletasks()  # 确保窗口大小已计算
            self.dropdown.deiconify()  # 显示窗口
            self.dropdown.attributes('-topmost', True)  # 确保菜单在最上层
            
            # 绑定事件
            self.dropdown.bind("<Leave>", self.on_menu_leave)
            self.winfo_toplevel().bind_all("<Button-1>", self.on_click_outside, "+")
        else:
            self.hide_dropdown()

    def on_menu_leave(self, event):
        """处理鼠标离开菜单事件"""
        if self.dropdown:
            # 获取当前鼠标位置
            x = self.dropdown.winfo_pointerx()
            y = self.dropdown.winfo_pointery()
            
            # 检查鼠标是否真的离开了菜单区域
            menu_x = self.dropdown.winfo_x()
            menu_y = self.dropdown.winfo_y()
            menu_width = self.dropdown.winfo_width()
            menu_height = self.dropdown.winfo_height()
            
            # 只有当鼠标真的离开菜单区域时才隐藏
            if not (menu_x <= x <= menu_x + menu_width and 
                   menu_y <= y <= menu_y + menu_height):
                self.dropdown.after(200, self.check_mouse_position)

    def check_mouse_position(self):
        """检查鼠标位置，决定是否隐藏菜单"""
        if self.dropdown:
            x = self.dropdown.winfo_pointerx()
            y = self.dropdown.winfo_pointery()
            menu_x = self.dropdown.winfo_x()
            menu_y = self.dropdown.winfo_y()
            menu_width = self.dropdown.winfo_width()
            menu_height = self.dropdown.winfo_height()
            
            if not (menu_x <= x <= menu_x + menu_width and 
                   menu_y <= y <= menu_y + menu_height):
                self.hide_dropdown()

    def on_click_outside(self, event):
        """处理点击其他区域事件"""
        if self.dropdown:
            x = event.x_root
            y = event.y_root
            menu_x = self.dropdown.winfo_x()
            menu_y = self.dropdown.winfo_y()
            menu_width = self.dropdown.winfo_width()
            menu_height = self.dropdown.winfo_height()
            
            if not (menu_x <= x <= menu_x + menu_width and 
                   menu_y <= y <= menu_y + menu_height):
                self.hide_dropdown()

    def hide_dropdown(self, event=None):
        """隐藏下拉菜单"""
        if self.dropdown:
            try:
                self.winfo_toplevel().unbind_all("<Button-1>")
                self.dropdown.destroy()
            except:
                pass
            finally:
                self.dropdown = None

    def execute_command(self, command):
        """执行菜单命令"""
        if command:
            self.hide_dropdown()
            command()

    def update_colors(self, colors):
        """更新菜单颜色"""
        self.colors = colors
        self.menu_button.configure(
            text_color=colors["text"],
            hover_color=colors["hover"]
        )

class TaskManager:
    def __init__(self, root):
        self.root = root
        self.version = "V0.1"
        
        # 设置窗口基本属性
        self.root.title(f"BoBoMaker 智能任务清单 {self.version}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 确保窗口已创建
        self.root.update_idletasks()
        
        # 定义展开/收起符号
        self.expand_symbols = {
            "expanded": "▼",
            "collapsed": "▶"
        }
        
        try:
            import ctypes
            from ctypes import windll, wintypes
            
            # 获取窗口句柄
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            
            # 定义窗口样式常量
            GWL_STYLE = -16
            GWL_EXSTYLE = -20
            WS_CAPTION = 0x00C00000
            WS_THICKFRAME = 0x00040000
            WS_EX_APPWINDOW = 0x00040000
            
            # 获取当前窗口样式
            style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            
            # 移除标题栏和边框
            style &= ~(WS_CAPTION | WS_THICKFRAME)
            
            # 设置新样式
            windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
            
            # 设置扩展样式，确保在任务栏显示
            exstyle = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            exstyle |= WS_EX_APPWINDOW
            windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, exstyle)
            
            # 强制更新窗口
            windll.user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                0x0002 | 0x0004 | 0x0020  # SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED
            )
            
        except Exception as e:
            print(f"Error setting window style: {str(e)}")
        
        # 设置主题
        ctk.set_default_color_theme("blue")
        
        # 定义亮色和暗色主题的颜色方案
        self.theme_colors = {
            "light": {
                "bg": "#FFFFFF",           # 纯白背景
                "sidebar": "#F8F9FA",      # 浅灰边栏
                "accent": "#4A90E2",       # 柔和的蓝色
                "text": "#2C3E50",         # 深灰文字
                "text_secondary": "#95A5A6",# 次要文字
                "border": "#E5E5E5",       # 边框颜色
                "hover": "#F1F5F9",        # 悬停颜色
                "completed": "#27AE60",    # 完成状态色
                "uncompleted": "#FFFFFF",  # 未完成状态色
                "titlebar": "#F8F9FA",     # 标题栏背景色
                "menubar": "#F8F9FA",      # 菜单栏背景色
                "container": "#F8F9FA",    # 容器背景色
                "selected": "#E6F0FF"      # 选中项背景色
            },
            "dark": {
                "bg": "#1A1B1E",           # 深色背景
                "sidebar": "#2D2D30",      # 深色侧边栏
                "accent": "#4A90E2",       # 保持相同的强调色
                "text": "#E0E0E0",         # 更亮的文字颜色
                "text_secondary": "#808080",# 次要文字颜色
                "border": "#3E3E42",       # 深色边框
                "hover": "#3E3E42",        # 深色悬停
                "completed": "#2ECC71",    # 亮色完成状态
                "uncompleted": "#2D2D30",  # 深色未完成状态
                "titlebar": "#252526",     # 更深的标题栏背景色
                "menubar": "#252526",      # 菜单栏背景色
                "container": "#252526",    # 容器背色
                "selected": "#2D3748"      # 选中项背景色
            }
        }
        
        # 加载主题设置
        self.load_theme_preference()
        
        # 创建自定义标题栏
        self.create_title_bar()
        
        # 绑定窗口事件
        self.root.bind("<Map>", self.on_map)
        self.root.bind("<Unmap>", self.on_unmap)
        
        # 加载创建任务数据
        self.categories = {
            "工作": [],
            "个人": [],
            "学习": [],
            "其他": []
        }
        self.current_category = "工作"
        self.selected_task = None
        
        self.drag_data = {"widget": None, "y": 0}
        self.drag_window = None
        
        # 最后设置窗口样式并显示
        self.setup_window()
        
        # 初始化界面
        self.setup_gui()
        self.load_tasks()

    def setup_gui(self):
        # 主容器
        self.main_frame = ctk.CTkFrame(self.root, fg_color=self.colors["bg"])
        self.main_frame.pack(fill="both", expand=True)
        
        # 创建自定义菜单栏
        self.create_menu_bar()
        
        # 要内容区域容器
        main_content = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左侧面板
        self.sidebar = ctk.CTkFrame(main_content, 
                                   width=120,
                                   fg_color=self.colors["sidebar"],
                                   border_width=1,
                                   border_color=self.colors["border"])
        self.sidebar.pack(side="left", fill="y", padx=(0, 5))
        self.sidebar.pack_propagate(False)
        
        # 类别标题
        self.category_title = ctk.CTkLabel(  # 保存为实例变量以便后续更新
            self.sidebar,
            text="任务类别",
            text_color=self.colors["text"],  # 使用主题文字颜色
            font=("微软雅黑", 13)
        )
        self.category_title.pack(pady=(15, 10))
        
        # 类别列表
        self.category_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.category_frame.pack(fill="both", expand=True, padx=10)
        
        self.category_buttons = []
        for category in self.categories:
            btn = ctk.CTkButton(self.category_frame,
                               text=category,
                               command=None,
                               fg_color="transparent",
                               text_color=self.colors["text"],
                               hover_color=self.colors["hover"],
                               anchor="w",
                               height=28,
                               font=("微软雅黑", 11))
            btn.pack(fill="x", pady=2)
            # 绑定键菜单和
            btn.bind("<Button-3>", lambda e, c=category: self.show_category_menu(e, c))
            btn.bind("<Button-1>", lambda e, b=btn, c=category: self.on_button_press(e, b, c))
            btn.bind("<B1-Motion>", self.on_drag_motion)
            btn.bind("<ButtonRelease-1>", self.on_button_release)
            self.category_buttons.append(btn)
        
        # 右侧任务区域
        self.right_pane = ctk.CTkFrame(main_content, 
                                      fg_color=self.colors["bg"],  # 使用主背景色
                                      border_width=1,
                                      border_color=self.colors["border"])
        self.right_pane.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        # 任务列表区域
        self.task_frame = ctk.CTkFrame(self.right_pane, 
                                      fg_color=self.colors["sidebar"])  # 使用侧边栏颜色
        self.task_frame.pack(side="left", fill="both", expand=True)
        
        # 任务输入框 - 简样式
        self.task_entry = ctk.CTkEntry(self.task_frame,
                                       placeholder_text="添加任务...",
                                       height=36,
                                       font=("微软雅黑", 11),
                                       border_color=self.colors["border"])
        self.task_entry.pack(fill="x", padx=15, pady=(15, 10))
        self.task_entry.bind('<Return>', self.add_task)
        
        # 任务列表滚动区域
        self.task_scroll = ctk.CTkScrollableFrame(self.task_frame,
                                                fg_color=self.colors["bg"])  # 改用主背景色
        self.task_scroll.pack(fill="both", expand=True, padx=20)
        
        # 任务详情面板（初始隐）
        self.detail_frame = ctk.CTkFrame(self.right_pane, 
                                       fg_color=self.colors["sidebar"],
                                       width=300)
        
    def select_category(self, category):
        # 确保类别存在
        if category in self.categories:
            self.current_category = category
            self.update_task_list()
            self.update_category_list()
        else:
            # 如果类别不存在，选择第一个可用的类别
            if self.categories:
                self.current_category = next(iter(self.categories))
            else:
                # 如果没有类别，创建默认类别
                self.categories = {
                    "工作": [],
                    "个人": [],
                    "学习": [],
                    "其他": []
                }
                self.current_category = "工作"
            self.update_task_list()
            self.update_category_list()

    def add_task(self, event=None):
        task_text = self.task_entry.get().strip()
        if task_text:
            task = {
                "text": task_text,
                "completed": False,
                "created_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "completed_date": None
            }
            self.categories[self.current_category].append(task)
            self.task_entry.delete(0, "end")
            self.update_task_list()
            self.save_tasks()
            self.update_category_list()
    
    def update_task_list(self):
        # 清除现有任务
        for widget in self.task_scroll.winfo_children():
            widget.destroy()
        
        tasks = self.categories[self.current_category]
        completed_tasks = [t for t in tasks if t["completed"]]
        uncompleted_tasks = [t for t in tasks if not t["completed"]]
        
        # 创建未完成任务分组
        if uncompleted_tasks:
            self.create_task_section("未完成", uncompleted_tasks, False)
        
        # 创建已完成任务分
        if completed_tasks:
            self.create_task_section("已完成", completed_tasks, True)
    
    def update_category_list(self):
        for btn, category in zip(self.category_buttons, self.categories):
            tasks = self.categories[category]
            completed = sum(1 for task in tasks if task["completed"])
            total = len(tasks)
            # 存储原始类别名称为按钮的属性
            btn._category_name = category
            btn.configure(text=f"{category} ({completed}/{total})")
            
            if category == self.current_category:
                btn.configure(fg_color=self.colors["accent"],
                            text_color="white",
                            hover_color=self.colors["accent"])
            else:
                btn.configure(fg_color="transparent",
                            text_color=self.colors["text"],
                            hover_color=self.colors["hover"])

    def save_tasks(self):
        with open("tasks.json", "w", encoding="utf-8") as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=2)
            
    def load_tasks(self):
        try:
            with open("tasks.json", "r", encoding="utf-8") as f:
                loaded_categories = json.load(f)
                # 更新任务数据格式
                for category, tasks in loaded_categories.items():
                    for task in tasks:
                        # 如果是旧格式的任务数据，添加新的字段
                        if "created_date" not in task:
                            task["created_date"] = task.get("date", datetime.now().strftime("%Y-%m-%d %H:%M"))
                        if "completed_date" not in task:
                            task["completed_date"] = task["created_date"] if task["completed"] else None
                self.categories = loaded_categories
                
                # 如果当前类别不存在择第一个可用的别
                if self.current_category not in self.categories:
                    self.current_category = next(iter(self.categories)) if self.categories else "工作"
                    
                # 如果没有任何类别，创建默认类别
                if not self.categories:
                    self.categories = {
                        "工作": [],
                        "个人": [],
                        "学习": [],
                        "其他": []
                    }
                    self.current_category = "工作"
                    
        except FileNotFoundError:
            # 如果件不存在，用默认类别
            self.categories = {
                "工作": [],
                "人": [],
                "学习": [],
                "其他": []
            }
            self.current_category = "工作"
        
        # 重新创建所有类别按钮
        self.repack_category_buttons()
        
        # 更新显示
        self.update_category_list()
        self.update_task_list()
        
    def add_category(self):
        dialog = ctk.CTkInputDialog(text="输入新类别名称:",
                                   title="添加类别")
        new_name = dialog.get_input()
        if new_name and new_name not in self.categories:
            self.categories[new_name] = []
            btn = ctk.CTkButton(self.category_frame,
                               text=new_name,
                               command=lambda c=new_name: self.select_category(c),
                               fg_color="transparent",
                               text_color=self.colors["text"],
                               hover_color=self.colors["hover"],
                               anchor="w",
                               height=28,
                               font=("微软雅黑", 11))
            btn.pack(fill="x", pady=2)
            self.category_buttons.append(btn)
            self.save_tasks()
            self.update_category_list()

    def edit_category(self):
        if not self.current_category:
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("重命名类")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设置大小并居中
        self.center_window(dialog, 400, 180)
        
        # 添加说明标签
        ctk.CTkLabel(dialog, 
                     text="输入新的类别名称:",
                     font=("微软雅黑", 12)).pack(pady=(15, 5))
        
        # 创输入框并预填充当前类别名称
        entry = ctk.CTkEntry(dialog, width=350)
        entry.pack(padx=20, pady=5)
        entry.insert(0, self.current_category)  # 预填充当前类别名称
        entry.select_range(0, 'end')  # 选中所有文本
        entry.focus()  # 获取焦点
        
        def save_changes():
            new_name = entry.get().strip()
            if new_name and new_name != self.current_category and new_name not in self.categories:
                # 获取所有类别的顺序
                categories = list(self.categories.items())
                # 到要重命名的类别的索引
                index = next(i for i, (cat, _) in enumerate(categories) if cat == self.current_category)
                # 重命名类别，保持其任务列表不变
                categories[index] = (new_name, self.categories[self.current_category])
                # 重建类别字典，保持顺序
                self.categories = dict(categories)
                
                # 更新当前选中的类别
                if self.current_category == self.current_category:
                    self.current_category = new_name
                
                # 重新创建按钮并更新显示
                self.repack_category_buttons()
                self.save_tasks()
            dialog.destroy()
        
        # 添加按钮
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        # 按钮容器，用于居中显示按钮
        buttons_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        buttons_container.pack(expand=True)
        
        # 确定按钮
        ctk.CTkButton(buttons_container,
                      text="确定",
                      command=save_changes,
                      width=80).pack(side="left", padx=10)
        
        # 取消按钮
        ctk.CTkButton(buttons_container,
                      text="取消",
                      command=dialog.destroy,
                      width=80).pack(side="left", padx=10)

    def toggle_task(self, task_index):
        task = self.categories[self.current_category][task_index]
        task["completed"] = not task["completed"]
        if task["completed"]:
            task["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            task["completed_date"] = None
        self.update_task_list()
        self.save_tasks()
        self.update_category_list()
        
    def create_task_section(self, title, tasks, is_completed=False):
        # 创建分组框架
        section_frame = ctk.CTkFrame(self.task_scroll, 
                                    fg_color="transparent")
        section_frame.pack(fill="x", pady=(0, 15))  # 增加底部间距
        
        # 创建标题行
        header_frame = ctk.CTkFrame(section_frame, 
                                   fg_color=self.colors["sidebar"],
                                   border_width=1,
                                   border_color=self.colors["border"])
        header_frame.pack(fill="x")
        
        # 展开/收起按钮
        expand_btn = ctk.CTkButton(header_frame,
                                  text=self.expand_symbols["expanded"],
                                  width=28,
                                  height=28,
                                  command=lambda: self.toggle_section(expand_btn, tasks_frame),
                                  fg_color="transparent",
                                  text_color=self.colors["text"],
                                  hover_color=self.colors["hover"],
                                  font=("微软雅黑", 12))
        expand_btn.pack(side="left", padx=(2, 2), pady=2)
        
        # 分组标题和任务数量
        title_text = f"{title} ({len(tasks)})"
        title_label = ctk.CTkLabel(header_frame,
                                  text=title_text,
                                  font=("微软雅黑", 14, "bold"),  # 保持标题字体大小
                                  text_color=self.colors["text"],
                                  anchor="w")
        title_label.pack(side="left", padx=(2, 5), pady=3)
        
        # 任务表框架
        tasks_frame = ctk.CTkFrame(section_frame, 
                                  fg_color="transparent")
        tasks_frame.pack(fill="x", pady=(5, 0))
        
        # 显示任务
        for i, task in enumerate(tasks):
            # 任务容器
            task_frame = ctk.CTkFrame(tasks_frame, 
                                     fg_color="transparent",
                                     height=45)  # 增加高度从40到45
            task_frame.pack(fill="x", pady=(0, 8))  # 增加任务间距
            task_frame.pack_propagate(False)
            
            # 任务内容容器
            content_frame = ctk.CTkFrame(task_frame,
                                       fg_color=self.colors["sidebar"],  # 改用 sidebar 颜色而不是 bg
                                       border_width=1,
                                       border_color=self.colors["border"])
            content_frame.pack(fill="both", padx=(25, 0))  # 添加左侧缩进
            
            # 任状态指示条
            status_bar = ctk.CTkFrame(content_frame,
                                    width=3,
                                    fg_color=self.colors["accent"] if not task["completed"] else "#999999")
            status_bar.pack(side="left", fill="y")
            
            # 复选框
            checkbox = ctk.CTkCheckBox(content_frame,
                                    text="",
                                    command=lambda i=i, completed=is_completed: 
                                        self.toggle_task(self.get_task_index(i, completed)),
                                    width=15,                    # 设置宽度为15
                                    height=15,                   # 设置高度15
                                    border_width=1,              # 保持框宽度为1
                                    corner_radius=7.5,           # 设置圆角半径为宽度的一半
                                    border_color=self.colors["border"] if not task["completed"] else self.colors["accent"],
                                    fg_color=self.colors["accent"],
                                    hover_color=self.colors["accent"],
                                    checkmark_color="white",     # 设置选标记颜色
                                    checkbox_width=15,           # 设置复选框宽度为15
                                    checkbox_height=15)          # 设置复选框高度为15
            checkbox.pack(side="left", padx=(10, 5), pady=5)
            checkbox.select() if task["completed"] else checkbox.deselect()
            
            # 任务信息容器
            info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=5)
            
            # 任务文本容器（于放置文本和删除线）
            text_container = ctk.CTkFrame(info_frame, fg_color="transparent")
            text_container.pack(side="top", fill="x")
            
            # 任务文本
            label = ctk.CTkLabel(text_container,
                                text=task["text"],
                                font=("微软雅黑", 14),
                                text_color="#AAAAAA" if task["completed"] else self.colors["text"],
                                wraplength=220,
                                justify="left",
                                anchor="w")
            label.pack(fill="x", padx=10, pady=5)  # 调整内边距从10到5
            
            # 加删除线效果
            if task["completed"]:
                # 等待标签渲染完成后添加删除线
                def add_strike_line():
                    # 获取文本标签的实际宽度
                    label.update_idletasks()  # 确保标签已完全渲染
                    
                    # 计算文本宽度（使用字符数估算）
                    text_width = len(task["text"]) * 14  # 每个字符大约14像素宽（根据字体大小）
                    
                    # 创建删除线
                    strike_line = ctk.CTkFrame(
                        text_container,
                        height=2,  # 删除线高度
                        width=text_width,  # 使用估算的文本宽度
                        fg_color="#808080" if self.theme_mode == "dark" else "#AAAAAA"
                    )
                    
                    # 计算删除线位置
                    label_height = label.winfo_height()
                    y_position = (label_height - 2) // 2  # 垂直居中
                    
                    # 放置删除线，与文本左对齐
                    strike_line.place(x=10, y=y_position)
                    strike_line.lift()  # 确保删除线在最上层
                
                # 延迟添加删除线，确保文本标签已完全渲染
                label.after(50, add_strike_line)
            
            # 任务时间和其他信息
            time_text = f"创建于 {task['created_date'].split(' ')[0]}"
            if task["completed"] and task["completed_date"]:
                time_text += f" · 完于 {task['completed_date'].split(' ')[0]}"
            
            time_label = ctk.CTkLabel(info_frame,
                                    text=time_text,
                                    font=("微软雅黑", 10),
                                    text_color=self.colors["text_secondary"],
                                    anchor="w")
            time_label.pack(side="top", fill="x", pady=(2, 0))
            
            # 绑定事件
            for widget in [content_frame, label, info_frame]:
                widget.bind("<Button-1>", lambda e, t=task, f=task_frame: self.show_task_details(t, f))
                widget.bind("<Button-3>", lambda e, t=task, i=i: self.show_task_menu(e, t, i))

    def toggle_section(self, button, content_frame):
        """处理任务分组的展开/收起，带动画效果"""
        is_expanded = button.cget("text") == self.expand_symbols["expanded"]
        
        if is_expanded:  # 当前是展开状态，需要收起
            # 保存当前高度
            current_height = content_frame.winfo_height()
            
            # 创建动画效果
            def animate_collapse(height):
                if height > 0:
                    # 设置新高度
                    content_frame.configure(height=height)
                    # 继续动画
                    self.root.after(10, lambda: animate_collapse(height - 20))
                else:
                    # 动画结束，隐藏内容
                    content_frame.pack_forget()
                    content_frame.configure(height=0)  # 设置为0而不是空字符串
                    button.configure(text=self.expand_symbols["collapsed"])
            
            # 开始收起动画
            content_frame.pack_propagate(False)
            animate_collapse(current_height)
            
        else:  # 当前是收起状态，需要展开
            # 先显示内容，但高度为0
            content_frame.pack(fill="x", pady=(5, 0))
            content_frame.pack_propagate(False)
            content_frame.configure(height=0)
            content_frame.update()
            
            # 临时设置为自然高度来获取所需高度
            content_frame.pack_propagate(True)
            natural_height = content_frame.winfo_reqheight()
            content_frame.pack_propagate(False)
            
            # 创建动画效果
            def animate_expand(height):
                if height < natural_height:
                    # 设置新高度
                    content_frame.configure(height=height)
                    # 继续动画
                    self.root.after(10, lambda: animate_expand(height + 20))
                else:
                    # 动画结束，恢复自然高度
                    content_frame.pack_propagate(True)
                    content_frame.configure(height=natural_height)  # 设置最终高度
                    button.configure(text=self.expand_symbols["expanded"])
            
            # 开始展开动画
            animate_expand(0)

    def get_task_index(self, section_index, is_completed):
        # 获取任在原始列表中的索引
        tasks = self.categories[self.current_category]
        completed_tasks = [t for t in tasks if t["completed"]]
        uncompleted_tasks = [t for t in tasks if not t["completed"]]
        
        if is_completed:
            task = completed_tasks[section_index]
        else:
            task = uncompleted_tasks[section_index]
        
        return tasks.index(task)
        
    def show_task_details(self, task, task_frame):
        # 检查是否点击的是当前显示的任务
        if (hasattr(self, 'detail_frame') and 
            hasattr(self, 'current_detail_task') and 
            self.detail_frame.winfo_exists() and 
            self.current_detail_task == task):
            # 如果是当前任务，则关闭详情面板
            self.hide_task_details()
            return
        
        # 如果已经有详情面板，先关闭它
        if hasattr(self, 'detail_frame') and self.detail_frame.winfo_exists():
            self.detail_frame.destroy()
        
        # 取消之前选中的任务的高亮
        if hasattr(self, 'last_selected_frame') and self.last_selected_frame:
            try:
                if self.last_selected_frame.winfo_exists():  # 检查框架是否仍然存在
                    self.last_selected_frame.configure(fg_color="transparent")
            except Exception:
                pass  # 如果框架不存在，忽略错误
        
        # 高亮当前选中的任务
        self.last_selected_frame = task_frame
        task_frame.configure(fg_color=self.colors["selected"])
        
        # 保存当前显示的任务
        self.current_detail_task = task
        
        # 创建新的详情面板
        self.detail_frame = ctk.CTkFrame(self.right_pane, 
                                       fg_color=self.colors["sidebar"],
                                       width=300)
        
        # 详情标题和关闭按钮容器
        title_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20,10))
        
        # 标题文字
        ctk.CTkLabel(title_frame,
                    text="任务详情",
                    text_color=self.colors["text"],
                    font=("微软雅黑", 16, "bold")).pack(side="left")
        
        # 关闭按钮
        close_btn = ctk.CTkButton(title_frame,
                                text="×",
                                width=20,
                                height=20,
                                command=self.hide_task_details,
                                fg_color="transparent",
                                text_color=self.colors["text"],
                                hover_color=self.colors["hover"],
                                font=("微软雅", 14))
        close_btn.pack(side="right")
        
        # 创建可滚动的内容区域
        content_scroll = ctk.CTkScrollableFrame(self.detail_frame, 
                                          fg_color="transparent")
        content_scroll.pack(fill="both", expand=True, padx=20)
        
        # 任务内容标签
        ctk.CTkLabel(content_scroll,
                    text="任务内容",
                    text_color=self.colors["text"],
                    font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(10,5))
        
        # 创建任务内容容器
        content_container = ctk.CTkFrame(content_scroll, 
                                       fg_color=self.colors["bg"],  # 使用主背景色
                                       border_width=1,
                                       border_color=self.colors["border"])
        content_container.pack(fill="x", pady=(0,15))
        
        # 任务内容文本（使用自动换行）
        content_label = ctk.CTkLabel(content_container,
                                   text=task["text"],
                                   text_color=self.colors["text"],
                                   font=("微软雅黑", 12),
                                   wraplength=220,  # 设置文本自动换行宽度
                                   justify="left",   # 左对齐
                                   anchor="w")       # 文本左对齐
        content_label.pack(fill="x", padx=10, pady=10)  # 添加内边距
        
        # 所属类别标签
        ctk.CTkLabel(content_scroll,
                    text="所属类别",
                    text_color=self.colors["text"],
                    font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(10,5))
        ctk.CTkLabel(content_scroll,
                    text=self.current_category,
                    text_color=self.colors["text"],
                    font=("微软雅黑", 12)).pack(anchor="w", pady=(0,10))
        
        # 创建时间标签
        ctk.CTkLabel(content_scroll,
                    text="创建时间",
                    text_color=self.colors["text"],
                    font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(10,5))
        ctk.CTkLabel(content_scroll,
                    text=task["created_date"],
                    text_color=self.colors["text"],
                    font=("微软雅黑", 12)).pack(anchor="w", pady=(0,10))
        
        # 完成时间标签
        ctk.CTkLabel(content_scroll,
                    text="完成时间",
                    text_color=self.colors["text"],
                    font=("微软雅黑", 12, "bold")).pack(anchor="w", pady=(10,5))
        completion_text = task["completed_date"] if task["completed"] else "未完成"
        ctk.CTkLabel(content_scroll,
                    text=completion_text,
                    text_color=self.colors["text"],
                    font=("微软雅黑", 12)).pack(anchor="w", pady=(0,10))
        
        # 详情面板
        self.detail_frame.pack(side="left", fill="y", padx=(10,0))

    def hide_task_details(self):
        """隐藏任务详情面板"""
        if hasattr(self, 'detail_frame') and self.detail_frame.winfo_exists():
            self.detail_frame.destroy()
        if hasattr(self, 'last_selected_frame') and self.last_selected_frame:
            try:
                if self.last_selected_frame.winfo_exists():
                    self.last_selected_frame.configure(fg_color="transparent")
            except Exception:
                pass
        # 清除���前显示的任务记录
        if hasattr(self, 'current_detail_task'):
            del self.current_detail_task

    # 添加创建菜单的方法
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 查看菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="查看", menu=view_menu)
        view_menu.add_command(label="切换主题 (亮/暗)", command=self.toggle_theme)  # 修改菜单项文本
        view_menu.add_separator()
        view_menu.add_command(label="刷新", command=self.refresh_view)
        
        # 任务菜单
        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="任务", menu=task_menu)
        task_menu.add_command(label="新建任务", command=lambda: self.task_entry.focus_set())
        task_menu.add_command(label="导入任务", command=self.import_tasks)
        task_menu.add_command(label="导出任务", command=self.export_tasks)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="数据备份", command=self.backup_data)
        tools_menu.add_command(label="数据恢复", command=self.restore_data)
        tools_menu.add_separator()
        tools_menu.add_command(label="清理已完成", command=self.clear_completed)
        
        # 帮助单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)

    # 添加菜单功能对应的方法
    def toggle_theme(self):
        """切换主题并更新所有组件的颜色"""
        # 切换主题式
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        
        # 先更新颜色方案
        self.colors = self.theme_colors[self.theme_mode]
        
        # 再更新外观模式
        ctk.set_appearance_mode(self.theme_mode)
        
        # 更新所有组件颜色
        self.update_theme_colors()
        
        # 保存当前主题设置
        self.save_theme_preference()
        
        # 更新菜单栏颜色
        self.menu_bar.configure(fg_color=self.colors["sidebar"])
        
        # 更新所有菜单按钮的颜色
        for widget in self.menu_bar.winfo_children():
            if isinstance(widget, ctk.CTkFrame):  # 菜单容器
                for menu in widget.winfo_children():
                    if isinstance(menu, CustomMenu):
                        menu.update_colors(self.colors)

    def update_theme_colors(self):
        """更新所有组件的颜色"""
        # 更新主窗口
        self.main_frame.configure(fg_color=self.colors["bg"])
        
        # 更新标题栏
        self.title_bar.configure(fg_color=self.colors["titlebar"])
        self.title_label.configure(text_color=self.colors["text"])
        self.min_btn.configure(text_color=self.colors["text"])
        self.close_btn.configure(text_color=self.colors["text"])
        
        # 更新菜单栏
        self.menu_bar.configure(fg_color=self.colors["sidebar"])
        # 更新侧边栏
        self.sidebar.configure(
            fg_color=self.colors["sidebar"],
            border_color=self.colors["border"]
        )
        
        # 更新右侧面板
        self.right_pane.configure(
            fg_color=self.colors["bg"],
            border_color=self.colors["border"]
        )
        
        # 更新任务列表区域
        self.task_frame.configure(
            fg_color=self.colors["sidebar"]
        )
        
        # 更新任务列表滚动区域
        self.task_scroll.configure(
            fg_color=self.colors["bg"]  # 使用主背景色
        )
        
        # 更新类别标题
        self.category_title.configure(text_color=self.colors["text"])
        
        # 更新类别按钮
        self.update_category_list()
        
        # 更新任务列表
        self.update_task_list()
        
        # 如果有任务详情面板，也需要更新它
        if hasattr(self, 'detail_frame') and self.detail_frame.winfo_exists():
            self.detail_frame.configure(fg_color=self.colors["sidebar"])
            # 更新内容容器的颜色
            for widget in self.detail_frame.winfo_children():
                if isinstance(widget, ctk.CTkScrollableFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkFrame) and child.cget("fg_color") == self.colors["bg"]:
                            child.configure(
                                fg_color=self.colors["bg"],
                                border_color=self.colors["border"]
                            )

    def save_theme_preference(self):
        """保存主题设置到配置文件"""
        try:
            with open("settings.json", "w") as f:
                json.dump({"theme": self.theme_mode}, f)
        except Exception as e:
            print(f"Error saving theme preference: {str(e)}")

    def load_theme_preference(self):
        """从��置文件载主题设置"""
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.theme_mode = settings.get("theme", "light")
                # 先设置颜色方案
                self.colors = self.theme_colors[self.theme_mode]
                # 再设置外观模式
                ctk.set_appearance_mode(self.theme_mode)
        except:
            # 如果配置文件不存在或出错，使用默认主题
            self.theme_mode = "light"
            self.colors = self.theme_colors[self.theme_mode]
            ctk.set_appearance_mode(self.theme_mode)

    def refresh_view(self):
        self.update_category_list()
        self.update_task_list()

    def import_tasks(self):
        # 实现导入任务功能
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择要导入的任务文件",
            filetypes=[("JSON 文件", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    imported_data = json.load(f)
                    self.categories.update(imported_data)
                    self.save_tasks()
                    self.update_category_list()
                    self.update_task_list()
            except Exception as e:
                self.show_message("导入失败", f"导入务时出错：{str(e)}")

    def export_tasks(self):
        # 实现导出任务功能
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="选择导出置",
            defaultextension=".json",
            filetypes=[("JSON 文", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.categories, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.show_message("失败", f"导出任务时出错：{str(e)}")

    def backup_data(self):
        # 实现数据备份
        from datetime import datetime
        backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, ensure_ascii=False, indent=2)
            self.show_message("备份成功", f"数据已备份至{backup_file}")
        except Exception as e:
            self.show_message("备份失败", f"备份数据时出错：{str(e)}")

    def restore_data(self):
        # 实现数据恢复功能
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择要恢复的备份文件",
            filetypes=[("JSON 文件", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
                    self.save_tasks()
                    self.update_category_list()
                    self.update_task_list()
                self.show_message("恢复成功", "数据已恢复")
            except Exception as e:
                self.show_message("复失败", f"恢复据出错：{str(e)}")

    def clear_completed(self):
        # 实现清理已完成任务功能
        if not self.show_confirm("确认清理", "确定要清理所有已完成的任务吗？"):
            return
        
        for category in self.categories:
            self.categories[category] = [
                task for task in self.categories[category]
                if not task["completed"]
            ]
        self.save_tasks()
        self.update_category_list()
        self.update_task_list()

    def show_help(self):
        self.show_message("使用说明", 
            "BoBoMaker 智��任务清单使用说明：\n\n"
            "1. 左侧面板显示任务类别\n"
            "2. 可以添编辑别\n"
            "3. 在输入框中输入任务按回车添加\n"
            "4. 点击复选标记任务完成状态\n"
            "5. 点击任务可查看详细信息\n"
            "6. 用菜单栏行更多操作"
        )

    def show_about(self):
        self.show_message("关于", 
            f"BoBoMaker 智能任务清单 {self.version}\n\n"
            "一个简单而强的任务管工具\n"
            "帮助您更好地组织和管理日常任务"
        )

    def show_message(self, title, message):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 先设置大小并居中
        self.center_window(dialog, 300, 150)
        
        # 添消息标签
        ctk.CTkLabel(dialog, 
                     text=message,
                     font=("微软雅黑", 12),
                     wraplength=250).pack(pady=(20, 20))
        
        # 确定按钮
        ctk.CTkButton(dialog,
                      text="确",
                      command=dialog.destroy,
                      width=80).pack(pady=(0, 20))

    def show_confirm(self, title, message):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 先设置大小并居中
        self.center_window(dialog, 300, 150)
        
        # 消息标签
        ctk.CTkLabel(dialog, 
                     text=message,
                     font=("微软雅黑", 12)).pack(pady=(20, 30))
        
        # 按钮框架
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        result = [False]  # 使用列表存储结果
        
        def on_confirm():
            result[0] = True
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # 确认和取消按钮
        ctk.CTkButton(button_frame, 
                      text="确定",
                      command=on_confirm,
                      width=80).pack(side="left", padx=10)
        ctk.CTkButton(button_frame,
                      text="取消",
                      command=on_cancel,
                      width=80).pack(side="left", padx=10)
        
        dialog.wait_window()  # 等待对话框关闭
        return result[0]

    # 添加示别菜单方法
    def show_category_menu(self, event, category):
        # 创建右键菜单
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="析", 
                        command=lambda: self.show_category_analysis(category))
        menu.add_command(label="重命名", 
                        command=lambda: self.rename_category(category))
        menu.add_command(label="删除", 
                        command=lambda: self.delete_category(category))
        
        # 设置菜单样式
        menu.configure(
            font=("微软雅黑", 10),
            bg=self.colors["sidebar"],
            fg=self.colors["text"],
            activebackground=self.colors["accent"],
            activeforeground="white"
        )
        
        # 显示单
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # 修改重名类别的方法
    def rename_category(self, category):
        # 创建自定义编辑对话框
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("重命名类别")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 置大小并居中
        self.center_window(dialog, 400, 180)
        
        # 添加明标签
        ctk.CTkLabel(dialog, 
                     text="输入新类���名称:",
                     font=("微软雅黑", 12)).pack(pady=(15, 5))
        
        # 创建输入框并预填充当前类别名称
        entry = ctk.CTkEntry(dialog, width=350)
        entry.pack(padx=20, pady=5)
        entry.insert(0, category)  # 预填充当前类别名称
        entry.select_range(0, 'end')  # 选中所有文本
        entry.focus()  # 获取焦点
        
        def save_changes():
            new_name = entry.get().strip()
            if new_name and new_name != category and new_name not in self.categories:
                # 获取所类别的顺序
                categories = list(self.categories.items())
                # 到要重命名的类别的索引
                index = next(i for i, (cat, _) in enumerate(categories) if cat == category)
                # 重命名类别，保持其任务列表不变
                categories[index] = (new_name, self.categories[category])
                # 重建类别字典，保持顺序
                self.categories = dict(categories)
                
                # 更新当前选中的类别
                if self.current_category == category:
                    self.current_category = new_name
                
                # 重新创建按钮并更新显示
                self.repack_category_buttons()
                self.save_tasks()
            dialog.destroy()
        
        # 添加按钮
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        # 按钮容器，用于居中显示按钮
        buttons_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        buttons_container.pack(expand=True)
        
        # 确定按钮
        ctk.CTkButton(buttons_container,
                      text="确定",
                      command=save_changes,
                      width=80).pack(side="left", padx=10)
        
        # 取消按钮
        ctk.CTkButton(buttons_container,
                      text="取消",
                      command=dialog.destroy,
                      width=80).pack(side="left", padx=10)

    # 添加类别删除方法
    def delete_category(self, category):
        if len(self.categories) <= 1:
            self.show_message("无法删除", "必须保留至少一个类别！")
            return
        
        if self.show_confirm("确认删除", f"确定要删除类别 '{category}' 吗？\n该类别下的所有任务都将被删除。"):
            del self.categories[category]
            if self.current_category == category:
                self.current_category = next(iter(self.categories))
            # 重创建所有类别按钮
            self.repack_category_buttons()
            # 保存更改
            self.save_tasks()
            # 更新显示
            self.update_category_list()
            self.update_task_list()

    # 添加数据分析窗口
    def show_category_analysis(self, category):
        analysis_window = ctk.CTkToplevel(self.root)
        analysis_window.title(f"类分析 - {category}")
        
        # 先设置大小居中
        self.center_window(analysis_window, 600, 400)
        
        # 获任务数据
        tasks = self.categories[category]
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task["completed"])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 按日期统计完成情况
        date_stats = {}
        for task in tasks:
            if task["completed"] and task["completed_date"]:
                date = task["completed_date"].split(" ")[0]  # 只取日期部分
                date_stats[date] = date_stats.get(date, 0) + 1
        
        # 创建内容框架
        content_frame = ctk.CTkFrame(analysis_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 总体统计
        stats_frame = ctk.CTkFrame(content_frame)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(stats_frame,
                     text="总体统计",
                     font=("微软黑", 16, "bold")).pack(pady=(10, 15))
        
        stats_text = (
            f"总任务数：{total_tasks}\n"
            f"已完成数：{completed_tasks}\n"
            f"完成率：{completion_rate:.1f}%"
        )
        
        ctk.CTkLabel(stats_frame,
                     text=stats_text,
                     font=("微软雅黑", 12)).pack(pady=(0, 10))
        
        # 日期计
        daily_frame = ctk.CTkFrame(content_frame)
        daily_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(daily_frame,
                     text="每日完成情况",
                     font=("微软雅黑", 16, "bold")).pack(pady=(10, 15))
        
        # 创建滚动区域显示每日计
        scroll_frame = ctk.CTkScrollableFrame(daily_frame)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 按日期倒序列
        for date in sorted(date_stats.keys(), reverse=True):
            count = date_stats[date]
            daily_text = f"{date}: 完成 {count} 个任务"
            ctk.CTkLabel(scroll_frame,
                        text=daily_text,
                        font=("微软雅黑", 12),
                        anchor="w").pack(fill="x", pady=2)
        
        # 如果没有完成记录
        if not date_stats:
            ctk.CTkLabel(scroll_frame,
                        text="暂完成记录",
                        font=("微软雅黑", 12),
                        text_color="gray").pack(pady=10)

    # 添加拖拽相关的方
    def on_button_press(self, event, widget, category):
        # 记录开始时间和位置
        self.press_data = {
            "time": event.time,
            "y": event.y_root,
            "widget": widget,
            "category": widget._category_name,
            "start_y": event.y_root  # 记录起始位置
        }

    def create_drag_window(self, widget, text):
        # 创建拖拽预览窗口
        if self.drag_window:
            self.drag_window.destroy()
        
        self.drag_window = tk.Toplevel(self.root)
        self.drag_window.overrideredirect(True)  # 边框窗口
        self.drag_window.attributes('-alpha', 0.7)  # 设置透明
        self.drag_window.attributes('-topmost', True)  # 保持在最上
        
        # 创建预览内容
        preview = ctk.CTkButton(self.drag_window,
                               text=text,
                               fg_color=self.colors["accent"],
                               text_color="white",
                               hover_color=self.colors["accent"],
                               width=widget.winfo_width(),
                               height=widget.winfo_height())
        preview.pack()

        # 定位预览窗口
        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        self.drag_window.geometry(f"+{x}+{y}")

    def on_drag_motion(self, event):
        if not hasattr(self, 'press_data') or not self.press_data:
            return
        
        # 检查是否已经拖拽足够长时间
        if event.time - self.press_data["time"] < 200:
            return
        
        widget = self.press_data["widget"]
        
        # 创建拖拽预览窗口
        if not self.drag_window and abs(event.y_root - self.press_data["start_y"]) > 10:
            self.is_dragging = True
            self.create_drag_window(widget, widget.cget("text"))
            # 隐藏原始按钮
            widget.pack_forget()
        
        if self.drag_window:
            # 移动预览窗口（使用整数坐标
            x = int(widget.winfo_rootx())
            y = int(event.y_root - widget.winfo_height()/2)
            self.drag_window.geometry(f"+{x}+{y}")
            
            # 计算目标位置
            current_index = self.category_buttons.index(widget)
            target_index = current_index
            
            # 清除之前的占位
            for w in self.category_frame.winfo_children():
                if isinstance(w, ctk.CTkFrame) and w not in self.category_buttons:
                    w.destroy()
            
            # 确保所有按钮都可见
            for btn in self.category_buttons:
                if btn != widget and not btn.winfo_viewable():
                    btn.pack(fill="x", pady=2)
            
            # 在目标位置创建空占位
            placeholder_height = widget.winfo_height() + 4
            
            # 遍历所有按钮找到目标位置
            found_target = False
            for i, btn in enumerate(self.category_buttons):
                if btn == widget:
                    continue
                btn_y = btn.winfo_rooty()
                if not found_target and event.y_root < btn_y + btn.winfo_height()/2:
                    target_index = i
                    # 在目标位置前插入空白
                    spacer = ctk.CTkFrame(self.category_frame, 
                                        height=placeholder_height,
                                        fg_color="transparent")
                    spacer.pack(fill="x", before=btn)
                    found_target = True
            
            # 如果鼠标在最后一个位置
            if not found_target:
                target_index = len(self.category_buttons)
                spacer = ctk.CTkFrame(self.category_frame,
                                    height=placeholder_height,
                                    fg_color="transparent")
                spacer.pack(fill="x")
            
            # 记录目标位置
            self.press_data["target_index"] = target_index

    def on_button_release(self, event):
        if not hasattr(self, 'press_data') or not self.press_data:
            return
        
        try:
            # 如果有生拖拽，则处理为点击事件
            if not hasattr(self, 'is_dragging') or not self.is_dragging:
                category = self.press_data["category"]
                self.select_category(category)
            else:
                # 如果发生了拖拽，更新顺序
                current_index = self.category_buttons.index(self.press_data["widget"])
                target_index = self.press_data.get("target_index", current_index)
                
                if target_index != current_index:
                    # 更新类别数据
                    categories = list(self.categories.items())
                    category = categories.pop(current_index)
                    categories.insert(target_index, category)
                    self.categories = dict(categories)
                
                # 重新创建所有按钮
                self.repack_category_buttons()
                self.save_tasks()
                self.update_category_list()
        finally:
            # 清理状态
            if self.drag_window:
                self.drag_window.destroy()
                self.drag_window = None
            # 清除所有临时的空白占位符
            for widget in self.category_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    widget.destroy()
            self.press_data = None
            self.is_dragging = False

    def repack_category_buttons(self):
        # 重新排列所有类别按钮并更新命令
        categories = list(self.categories.keys())
        
        # 清除所有按钮
        for btn in self.category_frame.winfo_children():
            btn.pack_forget()
        
        # 重新创建和排按钮
        self.category_buttons = []
        
        # 创建绑定事���的辅助函数
        def create_button_press_handler(btn, cat):
            return lambda e: self.on_button_press(e, btn, cat)
        
        def create_menu_handler(cat):
            return lambda e: self.show_category_menu(e, cat)
        
        for category in categories:
            btn = ctk.CTkButton(self.category_frame,
                               text=category,
                               command=None,
                               fg_color="transparent",
                               text_color=self.colors["text"],
                               hover_color=self.colors["hover"],
                               anchor="w",
                               height=28,
                               font=("微软雅黑", 11))
            btn.pack(fill="x", pady=2)
            
            # 使用辅助函数创建事件处理器
            btn.bind("<Button-3>", create_menu_handler(category))
            btn.bind("<Button-1>", create_button_press_handler(btn, category))
            btn.bind("<B1-Motion>", self.on_drag_motion)
            btn.bind("<ButtonRelease-1>", self.on_button_release)
            
            self.category_buttons.append(btn)
        
        # 新类别列表显示
        self.update_category_list()

    # 添加任务键菜单方法
    def show_task_menu(self, event, task, task_index):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="编辑", 
                        command=lambda: self.edit_task(task_index))
        menu.add_cascade(label="移动到", menu=self.create_move_menu(task_index))
        menu.add_command(label="删除",
                        command=lambda: self.delete_task(task_index))
        
        # 设置菜单样式
        menu.configure(
            font=("微软雅黑", 10),
            bg=self.colors["sidebar"],
            fg=self.colors["text"],
            activebackground=self.colors["accent"],
            activeforeground="white"
        )
        
        # 示菜单
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # 创移动到子菜单
    def create_move_menu(self, task_index):
        move_menu = tk.Menu(self.root, tearoff=0)
        
        # 设置子菜单样式
        move_menu.configure(
            font=("微软雅黑", 10),
            bg=self.colors["sidebar"],
            fg=self.colors["text"],
            activebackground=self.colors["accent"],
            activeforeground="white"
        )
        
        # 添加所有可用类
        for category in self.categories:
            if category != self.current_category:
                move_menu.add_command(
                    label=category,
                    command=lambda c=category: self.move_task(task_index, c)
                )
        
        return move_menu

    # 编辑任务
    def edit_task(self, task_index):
        task = self.categories[self.current_category][task_index]
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("编辑任务")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 先设置大小并居中
        self.center_window(dialog, 400, 180)
        
        # 添加说明标签
        ctk.CTkLabel(dialog, 
                     text="编辑任务内:",
                     font=("微软雅黑", 12)).pack(pady=(15, 5))  # 减小上边距
        
        # 创建输入框并预填充当前任务内容
        entry = ctk.CTkEntry(dialog, width=350)  # 增加输入框宽度
        entry.pack(padx=20, pady=5)  # 减内边距
        entry.insert(0, task["text"])
        entry.select_range(0, 'end')
        entry.focus()
        
        def save_changes():
            new_text = entry.get().strip()
            if new_text and new_text != task["text"]:
                task["text"] = new_text
                self.save_tasks()
                self.update_task_list()
            dialog.destroy()
        
        # 添加按钮
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 15))  # 调按钮区域的边距
        
        # 按钮容器，用于居中显示按钮
        buttons_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        buttons_container.pack(expand=True)
        
        # 确按钮
        ctk.CTkButton(buttons_container,
                      text="确定",
                      command=save_changes,
                      width=80).pack(side="left", padx=10)
        
        # 取消按钮
        ctk.CTkButton(buttons_container,
                      text="取消",
                      command=dialog.destroy,
                      width=80).pack(side="left", padx=10)

    # 移动任务到其他类别
    def move_task(self, task_index, target_category):
        task = self.categories[self.current_category].pop(task_index)
        self.categories[target_category].append(task)
        self.save_tasks()
        self.update_task_list()
        self.update_category_list()

    # 删除任务
    def delete_task(self, task_index):
        if self.show_confirm("确认删除", "确定要删除这个任务吗？"):
            self.categories[self.current_category].pop(task_index)
            self.save_tasks()
            self.update_task_list()
            self.update_category_list()

    # 在 TaskManager 类中添加窗口居中方法
    def center_window(self, window, width=None, height=None):
        # 如果没指定大小，取窗口当前大小
        if width is None:
            width = window.winfo_width()
        if height is None:
            height = window.winfo_height()
        
        # 获取屏幕尺寸
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置
        window.geometry(f"{width}x{height}+{x}+{y}")

    def create_title_bar(self):
        # 创建自定义标题栏
        self.title_bar = ctk.CTkFrame(self.root, 
                                     height=35,
                                     fg_color=self.colors["titlebar"])
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        # 图标和标题
        title_text = f"BoBoMaker 智能任务清单 {self.version}"
        self.title_label = ctk.CTkLabel(self.title_bar,  # 保存为���例变量以便后续更新
                              text=title_text,
                              font=("微软雅黑", 12),
                              text_color=self.colors["text"])  # 使用主题文字颜色
        self.title_label.pack(side="left", padx=10)
        
        # 窗口控制按钮容器
        btn_container = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        btn_container.pack(side="right", padx=5)
        
        # 最小化按钮
        self.min_btn = ctk.CTkButton(btn_container,  # 保存为实例变量
                           text="—",
                           width=35,
                           height=25,
                           command=lambda: self.root.iconify(),
                           fg_color="transparent",
                           text_color=self.colors["text"],  # 使用主题文字颜色
                           hover_color=self.colors["hover"])
        self.min_btn.pack(side="left", padx=2)
        
        # 关闭按钮
        self.close_btn = ctk.CTkButton(btn_container,  # 保存为实例变量
                             text="×",
                             width=35,
                             height=25,
                             command=self.on_closing,
                             fg_color="transparent",
                             text_color=self.colors["text"],  # 使用主题文字颜色
                             hover_color="#FF4757")
        self.close_btn.pack(side="left", padx=2)
        
        # 绑定拖动事件
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<Button-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        """处理窗口拖动开始"""
        try:
            from ctypes import windll
            
            # 获取窗口句柄
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            
            # 用 PostMessage 代 SendMessage
            windll.user32.ReleaseCapture()
            windll.user32.PostMessageW(hwnd, 0xA1, 2, 0)
            
        except Exception as e:
            print(f"Error in start_move: {str(e)}")
            # 如果上述方法失败，使用传统方法
            self.x = event.x
            self.y = event.y

    def do_move(self, event):
        """处理窗口拖动"""
        # 只有传统方法时才需要这个函数
        if hasattr(self, 'x') and hasattr(self, 'y'):
            try:
                deltax = event.x - self.x
                deltay = event.y - self.y
                x = self.root.winfo_x() + deltax
                y = self.root.winfo_y() + deltay
                self.root.geometry(f"+{x}+{y}")
            except Exception as e:
                print(f"Error in do_move: {str(e)}")

    # 将 create_menu_bar 方法移动到类内部
    def create_menu_bar(self):
        # 创建菜单栏容器
        self.menu_bar = ctk.CTkFrame(
            self.main_frame,
            height=30,
            fg_color=self.colors["sidebar"],  # 使用侧边栏颜色
            border_width=1,
            border_color=self.colors["border"]
        )
        self.menu_bar.pack(fill="x", side="top")
        self.menu_bar.pack_propagate(False)
        
        # 创建菜单项容器
        menu_container = ctk.CTkFrame(
            self.menu_bar,
            fg_color="transparent"
        )
        menu_container.pack(side="left", padx=5)
        
        # 查看菜单
        view_menu = CustomMenu(
            menu_container,
            "查看",
            {
                "切换主题 (亮/暗)": self.toggle_theme,
                "-": None,
                "刷新": self.refresh_view
            },
            self.colors
        )
        view_menu.pack(side="left", padx=2)
        
        # 任务菜单
        task_menu = CustomMenu(
            menu_container,
            "任务",
            {
                "新建任务": lambda: self.task_entry.focus_set(),
                "导入任务": self.import_tasks,
                "导出任务": self.export_tasks
            },
            self.colors
        )
        task_menu.pack(side="left", padx=2)
        
        # 工具菜单
        tools_menu = CustomMenu(
            menu_container,
            "工具",
            {
                "数据备份": self.backup_data,
                "数据恢复": self.restore_data,
                "-": None,
                "清理已完成": self.clear_completed
            },
            self.colors
        )
        tools_menu.pack(side="left", padx=2)
        
        # 帮助菜单
        help_menu = CustomMenu(
            menu_container,
            "帮助",
            {
                "使用说明": self.show_help,
                "关于": self.show_about
            },
            self.colors
        )
        help_menu.pack(side="left", padx=2)

    def on_closing(self):
        """处理窗口关闭事件"""
        try:
            self.save_tasks()  # 保存数据
            self.root.quit()   # 退出程序
        except:
            self.root.quit()   # 如果保存失败也要确保程序能够退出

    def minimize_window(self):
        """处理最小化事件"""
        self.root.iconify()

    def on_map(self, event):
        """处理窗口恢复事件"""
        pass  # 不需要特殊处理

    def on_unmap(self, event):
        """处理窗口最小化事件"""
        pass  # 不需要特殊处理

    def setup_window(self):
        """设置窗样式和属性"""
        pass  # 不再需要这个方法

if __name__ == "__main__":
    try:
        root = ctk.CTk()
        app = TaskManager(root)
        app.center_window(root, 900, 600)
        root.mainloop()
    except KeyboardInterrupt:
        root.quit() 