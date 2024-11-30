import tkinter as tk
import customtkinter as ctk
import json
from datetime import datetime
import sqlite3
from PIL import Image
import tkinter.font as tkFont
from PIL import ImageTk  # 添加 ImageTk 的导入
import os
import sys
import webbrowser

def get_resource_path(relative_path):
    """ 获取资源文件的绝对路径 """
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

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
            self.dropdown.configure(bg=self.colors["sidebar"])
            
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
            self.dropdown.update_idletasks()
            self.dropdown.deiconify()
            self.dropdown.attributes('-topmost', True)
            
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
        self.version = "V1.2"
        
        # 设置窗口图标
        try:
            # 加载并转换图标
            icon_path = get_resource_path("logo.png")
            icon_image = Image.open(icon_path)
            # 创建临时ico文件
            icon_image = icon_image.resize((32, 32))  # Windows图标推荐尺寸
            
            # 如果图片是PNG格式且有透明通道，需要确保它有RGBA模式
            if 'A' not in icon_image.mode:
                icon_image = icon_image.convert('RGBA')
            
            # 保存为临时ico文件
            icon_image.save("temp_icon.ico", format='ICO', sizes=[(32, 32)])
            
            # 设置窗口图标
            self.root.iconbitmap("temp_icon.ico")
            
            # 删除临时文件
            os.remove("temp_icon.ico")
        except Exception as e:
            print(f"Error setting window icon: {str(e)}")
        
        # 初始化数据库
        self.init_database()
        
        # 设置窗口基本属性
        self.root.title(f"BoBoMaker 智能清单 {self.version}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 确保窗口已创建
        self.root.update_idletasks()
        
        # 加载主题图标
        self.theme_icons = {
            "light": ctk.CTkImage(
                light_image=Image.open(get_resource_path("icons/moon.png")),
                dark_image=Image.open(get_resource_path("icons/moon.png")),
                size=(20, 20)
            ),
            "dark": ctk.CTkImage(
                light_image=Image.open(get_resource_path("icons/sun.png")),
                dark_image=Image.open(get_resource_path("icons/sun.png")),
                size=(20, 20)
            )
        }
        
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
            
            #口样式
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
                "text": "#2C3E50",         # 深颜色的字
                "text_secondary": "#95A5A6",# 次要文字颜色
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
                "titlebar": "#252526",     # 更深的标题背景色
                "menubar": "#252526",      # 菜单背景色
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
        
        # 添加窗口停靠相关的属性
        self.is_docked = False
        self.is_dragging = False  # 添加拖动状态标志
        self.dock_timer = None
        self.hide_timer = None
        self.show_timer = None
        self.dock_height = 5  # 隐藏时露出的高度
        self.dock_width = 350  # 使用固定的停靠宽度
        self.original_geometry = None  # 保存原始位置和大小
        
        # 绑定鼠标进入和离开事件
        self.root.bind("<Enter>", self.on_mouse_enter)
        self.root.bind("<Leave>", self.on_mouse_leave)

    def init_database(self):
        """初始化数据库"""
        try:
            self.conn = sqlite3.connect('bobomaker.db')
            self.cursor = self.conn.cursor()
            
            # 创建类别表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    position INTEGER NOT NULL
                )
            ''')
            
            # 创建任务表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    text TEXT NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT 0,
                    created_date TEXT NOT NULL,
                    completed_date TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            
            # 创建设置表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            self.conn.commit()
        except Exception as e:
            print(f"Database initialization error: {str(e)}")

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
                                   width=120,  # 设置固定的初始宽度
                                   fg_color=self.colors["sidebar"],
                                   border_width=1,
                                   border_color=self.colors["border"])
        self.sidebar.pack(side="left", fill="y", padx=(0, 5))
        self.sidebar.pack_propagate(False)
        
        # 初始化侧边栏状态
        self.is_animating = False
        self.is_expanded = True
        self.sidebar_width = 120
        self.max_width = 120  # 在这里初始化 max_width
        self.animation_id = None
        
        # 创建标题栏框架并保存引用
        self.title_bar_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.title_bar_frame.pack(fill="x", pady=(15, 10))
        
        # 类别标题
        self.category_title = ctk.CTkLabel(
            self.title_bar_frame,
            text="任务类别",
            text_color=self.colors["text"],
            font=("微软雅黑", 13)
        )
        self.category_title.pack(side="left", padx=10)
        
        # 添加展开/收起按钮
        self.sidebar_toggle_btn = ctk.CTkButton(
            self.title_bar_frame,
            text="◀",  # 使用左箭头表示可以收起
            width=20,
            height=20,
            corner_radius=5,
            fg_color="transparent",
            text_color=self.colors["text"],
            hover_color=self.colors["hover"],
            font=("微软雅黑", 12),
            command=self.toggle_sidebar
        )
        self.sidebar_toggle_btn.pack(side="right", padx=5)
        
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
            # 绑定菜单和按钮事件
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
        
        # 任务详情面板初始隐藏
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
        """添加新任务"""
        task_text = self.task_entry.get().strip()
        if task_text:
            try:
                # 创建新任务
                task = {
                    "text": task_text,
                    "completed": False,
                    "created_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "completed_date": None
                }
                
                # 添加到当前类别
                if self.current_category not in self.categories:
                    self.categories[self.current_category] = []
                self.categories[self.current_category].append(task)
                
                # 清空输入框
                self.task_entry.delete(0, "end")
                
                # 保存到数据库
                try:
                    # 获取类别ID
                    self.cursor.execute('SELECT id FROM categories WHERE name = ?', 
                                      (self.current_category,))
                    category_id = self.cursor.fetchone()
                    
                    if category_id is None:
                        # 如果类别不存在，先创建类别
                        self.cursor.execute('''
                            INSERT INTO categories (name, position) 
                            VALUES (?, (SELECT COALESCE(MAX(position), 0) + 1 FROM categories))
                        ''', (self.current_category,))
                        category_id = self.cursor.lastrowid
                    else:
                        category_id = category_id[0]
                    
                    # 插入任务
                    self.cursor.execute('''
                        INSERT INTO tasks (category_id, text, completed, created_date, completed_date)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (category_id, task["text"], task["completed"], 
                         task["created_date"], task["completed_date"]))
                    
                    self.conn.commit()
                except Exception as e:
                    print(f"Error saving task to database: {str(e)}")
                    self.conn.rollback()
                
                # 更新显示
                self.update_task_list()
                self.update_category_list()
                
            except Exception as e:
                print(f"Error adding task: {str(e)}")

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
        """保存任务到数据库"""
        try:
            # 开始事务
            self.cursor.execute('BEGIN TRANSACTION')
            
            # 清空现有数据
            self.cursor.execute('DELETE FROM tasks')
            self.cursor.execute('DELETE FROM categories')
            
            # 保存类别和任务
            for position, (category_name, tasks) in enumerate(self.categories.items()):
                # 插入类别（只插入一次）
                self.cursor.execute(
                    'INSERT INTO categories (name, position) VALUES (?, ?)',
                    (category_name, position)
                )
                category_id = self.cursor.lastrowid
                
                # 保存该类别下的所有任务
                for task in tasks:
                    self.cursor.execute('''
                        INSERT INTO tasks (
                            category_id, text, completed, 
                            created_date, completed_date
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        category_id,
                        task['text'],
                        1 if task['completed'] else 0,  # 确保布尔值正确保存
                        task['created_date'],
                        task['completed_date']
                    ))
            
            # 提交事务
            self.conn.commit()
        except Exception as e:
            print(f"Error saving tasks: {str(e)}")
            self.conn.rollback()

    def load_tasks(self):
        """从数据库加载任务"""
        try:
            # 清空现有数据
            self.categories = {}
            
            # 加载所有类别
            self.cursor.execute('''
                SELECT id, name, position FROM categories 
                ORDER BY position
            ''')
            categories = self.cursor.fetchall()
            
            # 如果没有类别，创建默认类别
            if not categories:
                default_categories = ["工作", "个人", "学习", "其他"]
                for i, category in enumerate(default_categories):
                    self.cursor.execute('''
                        INSERT INTO categories (name, position) VALUES (?, ?)
                    ''', (category, i))
                self.conn.commit()
                
                # 重新加载类别
                self.cursor.execute('''
                    SELECT id, name, position FROM categories 
                    ORDER BY position
                ''')
                categories = self.cursor.fetchall()
            
            # 初始化类别字典
            for category_id, category_name, _ in categories:
                self.categories[category_name] = []
                
                # 加载该类别的所有任务
                self.cursor.execute('''
                    SELECT text, completed, created_date, completed_date 
                    FROM tasks 
                    WHERE category_id = ?
                ''', (category_id,))
                
                tasks = self.cursor.fetchall()
                for task_data in tasks:
                    self.categories[category_name].append({
                        'text': task_data[0],
                        'completed': bool(task_data[1]),
                        'created_date': task_data[2],
                        'completed_date': task_data[3]
                    })
            
            # 设置当前类别
            if not self.current_category or self.current_category not in self.categories:
                self.current_category = next(iter(self.categories))
            
            # 更新显示
            self.update_category_list()
            self.update_task_list()
            
        except Exception as e:
            print(f"Error loading tasks: {str(e)}")
            # 使用默认类别
            self.categories = {
                "工作": [],
                "个人": [],
                "学习": [],
                "其他": []
            }
            self.current_category = "工作"
            self.update_category_list()
            self.update_task_list()
        
        # 重新创建所有类别按钮
        self.repack_category_buttons()
        
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
        
        # 类别名称标签
        ctk.CTkLabel(dialog, 
                     text="输入新的类别名称:",
                     font=("微软雅黑", 12)).pack(pady=(15, 5))
        
        # 创建输入框并预填充当前类别名称
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
                
                # 更新当前选中类别
                if self.current_category == self.current_category:
                    self.current_category = new_name
                
                # 重新创建按钮并更新显示
                self.repack_category_buttons()
                self.save_tasks()
            dialog.destroy()
        
        # 添加按钮
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        # 按钮器，于居中显示钮
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
        """切换任务状态"""
        try:
            # 获取当前类别的所有任务
            tasks = self.categories[self.current_category]
            
            # 确保任务索引有效
            if 0 <= task_index < len(tasks):
                task = tasks[task_index]
                # 切换状态
                task["completed"] = not task["completed"]
                
                # 更新完成时间
                if task["completed"]:
                    task["completed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                else:
                    task["completed_date"] = None
                
                # 保存更改
                self.save_tasks()
                
                # 更新显示
                self.update_task_list()
                self.update_category_list()
                
                # 如果有详情面板打开，也需要更新它
                if (hasattr(self, 'detail_frame') and 
                    hasattr(self, 'current_detail_task') and 
                    self.detail_frame.winfo_exists() and 
                    self.current_detail_task == task):
                    self.hide_task_details()
                    
        except Exception as e:
            print(f"Error toggling task: {str(e)}")

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
                                     fg_color="transparent")
            task_frame.pack(fill="x", pady=(0, 8))
            
            # 任务内容容器
            content_frame = ctk.CTkFrame(task_frame,
                                       fg_color=self.colors["sidebar"],
                                       border_width=1,
                                       border_color=self.colors["border"])
            content_frame.pack(fill="x", padx=(25, 0))
            
            # 任务状态指示条
            status_bar = ctk.CTkFrame(content_frame,
                                    width=3,
                                    height=28,  # 设置固定高度
                                    fg_color=self.colors["accent"] if not task["completed"] else "#999999")
            status_bar.pack(side="left")  # 移除 fill="y"
            status_bar.pack_propagate(False)  # 保持固定大小
            
            # 复选框
            checkbox = ctk.CTkCheckBox(content_frame,
                                    text="",
                                    width=15,
                                    height=15,
                                    border_width=1,
                                    corner_radius=7.5,
                                    border_color=self.colors["border"] if not task["completed"] else self.colors["accent"],
                                    fg_color=self.colors["accent"],
                                    hover_color=self.colors["accent"],
                                    checkmark_color="white",
                                    checkbox_width=15,
                                    checkbox_height=15)
            checkbox.pack(side="left", padx=(10, 5))
            
            # 设置初始状态
            if task["completed"]:
                checkbox.select()
            else:
                checkbox.deselect()
            
            # 获取任务在原始列表中的索引
            original_index = self.categories[self.current_category].index(task)
            
            # 绑定命令
            checkbox.configure(command=lambda idx=original_index: self.toggle_task(idx))
            
            # 计算可用宽度
            available_width = content_frame.winfo_width() - 60  # 减去状态条、复选框和内边距的宽度
            
            # 使用 CTkFont 而不是 tkFont
            task_font = ctk.CTkFont(
                family="微软雅黑",
                size=14,
                slant="roman"
            )
            
            # 任务文本
            text = task["text"]
            if task["completed"]:
                # 方法1：使用双重删除线
                text = ''.join([char + '\u0336\u0336' for char in text])
                
                # 或者方法2：使用粗删除线字符
                # text = ''.join([char + '\u0335' for char in text])  # \u0335 是一个更粗的删除线字符
            
            # 任务文本标签
            label = ctk.CTkLabel(content_frame,
                                text=text,
                                font=task_font,
                                text_color="#AAAAAA" if task["completed"] else self.colors["text"],
                                wraplength=400,  # 先设置一个初始值
                                justify="left",
                                anchor="w")
            label.pack(side="left", 
                      fill="x",
                      expand=True,  # 改回 True，让标签能够占据可用空间
                      padx=(5, 10),
                      pady=(4, 4))
            
            def update_wraplength(label=label, content_frame=content_frame):
                try:
                    # 计算实际可用宽度
                    content_width = content_frame.winfo_width()
                    if content_width > 0:
                        # 减去左侧状态条、复选框和内边距的宽度
                        available_width = content_width - 60
                        if available_width > 0:
                            label.configure(wraplength=available_width)
                            # 强制更新布局
                            label.update_idletasks()
                            content_frame.update_idletasks()
                    # 删除这行，不要再次调度更新
                    # label.after(100, lambda: update_wraplength(label, content_frame))
                except Exception as e:
                    print(f"Error updating wraplength: {str(e)}")
            
            # 绑定大小变化事件
            content_frame.bind('<Configure>', lambda e, l=label, c=content_frame: update_wraplength(l, c))
            
            # 立即调用一次更新
            self.root.after(10, lambda: update_wraplength(label, content_frame))
            
            # 绑定事件
            for widget in [content_frame, label]:
                widget.bind("<Button-1>", lambda e, t=task, f=task_frame: self.show_task_details(t, f))
                widget.bind("<Button-3>", lambda e, t=task, i=i: self.show_task_menu(e, t, i))

    def toggle_section(self, button, content_frame):
        """处理任务分组的展开/收起"""
        is_expanded = button.cget("text") == self.expand_symbols["expanded"]
        
        # 临时解绑 Configure 事件，避免触发不必要的更新
        for widget in content_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.unbind('<Configure>')
        
        if is_expanded:  # 当前是展开状态，需要收起
            content_frame.pack_forget()
            button.configure(text=self.expand_symbols["collapsed"])
        else:  # 当前是收起状态，需要展开
            content_frame.pack(fill="x", pady=(5, 0))
            button.configure(text=self.expand_symbols["expanded"])
        
        # 完成后重新绑定事件
        for widget in content_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.bind('<Configure>', 
                           lambda e, l=widget, c=content_frame: self.update_wraplength(l, c))

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
            self.hide_task_details()
            return
        
        # 如果已经有详情面板，先关闭它
        if hasattr(self, 'detail_frame') and self.detail_frame.winfo_exists():
            self.detail_frame.destroy()
        
        # 取消之前选中的任务的高亮
        if hasattr(self, 'last_selected_frame') and self.last_selected_frame:
            try:
                if self.last_selected_frame.winfo_exists():
                    self.last_selected_frame.configure(fg_color="transparent")
            except Exception:
                pass
        
        # 高亮当前选中的任务
        self.last_selected_frame = task_frame
        task_frame.configure(fg_color=self.colors["selected"])
        
        # 保存当前显示的任务
        self.current_detail_task = task
        
        # 创建详情面板
        self.detail_frame = ctk.CTkFrame(self.right_pane, 
                                   fg_color=self.colors["sidebar"],
                                   width=300)
        
        # 内容区域
        content_frame = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 顶部任务状态和内容
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # 复选框
        def on_checkbox_click():
            # 获取任务在列表中的索引
            tasks = self.categories[self.current_category]
            task_index = tasks.index(task)
            # 切换任务状态
            self.toggle_task(task_index)
            # 更新任务列表
            self.update_task_list()
            # 关闭详情面板
            self.hide_task_details()
        
        checkbox = ctk.CTkCheckBox(header_frame,
                                  text="",
                                  command=on_checkbox_click,
                                  width=15,
                                  height=15,
                                  border_width=1,
                                  corner_radius=7.5,
                                  border_color=self.colors["border"] if not task["completed"] else self.colors["accent"],
                                  fg_color=self.colors["accent"],
                                  hover_color=self.colors["accent"],
                                  checkmark_color="white",
                                  checkbox_width=15,
                                  checkbox_height=15)
        checkbox.pack(side="left", anchor="n", pady=3)
        if task["completed"]:
            checkbox.select()
        
        # 任务内容容器
        content_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        content_container.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # 任务内容标签（默认显示）
        self.content_label = ctk.CTkLabel(
            content_container,
            text=task["text"],
            text_color=self.colors["text"],
            font=("微软雅黑", 14, "bold"),
            wraplength=250,
            justify="left",
            anchor="w",
            cursor="hand2"  # 显示手型光标表示可点击
        )
        self.content_label.pack(fill="x")
        
        # 任务内容输入框（初始隐藏）
        self.content_entry = ctk.CTkTextbox(
            content_container,
            text_color=self.colors["text"],
            font=("微软雅黑", 14, "bold"),
            fg_color="transparent",
            border_width=0,
            height=100,  # 设置适当的高度
            width=250
        )
        self.content_entry.insert("1.0", task["text"])

        def start_edit(event=None):
            # 隐藏标签，显示输入框
            self.content_label.pack_forget()
            self.content_entry.pack(fill="x", expand=True)  # 添加 expand=True 使文本框可以扩展
            self.content_entry.focus()
            return "break"  # 阻止事件继续传播
        
        def save_edit(event=None):
            new_text = self.content_entry.get("1.0", "end-1c").strip()  # 获取文本框的所有内容
            if new_text and new_text != task["text"]:
                # 获取任务在列表中的索引
                tasks = self.categories[self.current_category]
                task_index = tasks.index(task)
                # 更新任务文本
                task["text"] = new_text
                # 更新标签文本
                self.content_label.configure(text=new_text)
                # 保存更改
                self.save_tasks()
                # 更新任务列表显示
                self.update_task_list()
                # 更新类别列表（如果需要）
                self.update_category_list()
            
            # 隐藏输入框，显示标签
            self.content_entry.pack_forget()
            self.content_label.pack(fill="x")
            return "break"
        
        def cancel_edit(event=None):
            # 取消编辑，恢复原文本
            self.content_entry.pack_forget()
            self.content_label.pack(fill="x")
            return "break"
        
        # 绑事件
        self.content_label.bind("<Button-1>", start_edit)  # 点击开始编辑
        self.content_entry.bind("<Return>", save_edit)     # 回车保存
        self.content_entry.bind("<FocusOut>", save_edit)   # 失去焦点时保存
        self.content_entry.bind("<Escape>", cancel_edit)   # ESC取消编辑
        
        # 任务信息
        info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, 10))
        
        # 所属清单
        list_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        list_frame.pack(fill="x", pady=(0, 15))
        list_label = ctk.CTkLabel(list_frame,
                                 text="所属清单",
                                 text_color=self.colors["text_secondary"],
                                 font=("微软雅黑", 12))
        list_label.pack(side="left", padx=(0, 15))
        list_value = ctk.CTkLabel(list_frame,
                                 text=self.current_category,
                                 text_color=self.colors["text"],
                                 font=("微软雅黑", 12))
        list_value.pack(side="left")
        
        # 创建时间
        create_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        create_frame.pack(fill="x", pady=(0, 15))
        create_label = ctk.CTkLabel(create_frame,
                                   text="创建时间",
                                   text_color=self.colors["text_secondary"],
                                   font=("微软雅黑", 12))
        create_label.pack(side="left", padx=(0, 15))
        create_value = ctk.CTkLabel(create_frame,
                                   text=task["created_date"],
                                   text_color=self.colors["text"],
                                   font=("微软雅黑", 12))
        create_value.pack(side="left")
        
        # 完成时间
        complete_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        complete_frame.pack(fill="x")
        complete_label = ctk.CTkLabel(complete_frame,
                                     text="完成时间",
                                     text_color=self.colors["text_secondary"],
                                     font=("微软雅黑", 12))
        complete_label.pack(side="left", padx=(0, 15))
        completion_text = task["completed_date"] if task["completed"] else "未完成"
        complete_value = ctk.CTkLabel(complete_frame,
                                     text=completion_text,
                                     text_color=self.colors["text"],
                                     font=("微软雅黑", 12))
        complete_value.pack(side="left")
        
        # 修改点击外部区域关闭详情的逻辑
        def on_click_outside(event):
            try:
                # 确保详情面板还存在
                if not hasattr(self, 'detail_frame') or not self.detail_frame.winfo_exists():
                    self.root.unbind_all("<Button-1>")
                    return
                
                # 获取点击位置相对于详情面板的坐标
                x = event.x_root - self.detail_frame.winfo_rootx()
                y = event.y_root - self.detail_frame.winfo_rooty()
                
                # 检查点击是否在详情面板外
                if not (0 <= x <= self.detail_frame.winfo_width() and 
                        0 <= y <= self.detail_frame.winfo_height()):
                    self.hide_task_details()
                    # 解绑点击事件
                    self.root.unbind_all("<Button-1>")
            except Exception as e:
                # 如果发生错误，安全地关闭详情面板
                if hasattr(self, 'detail_frame') and self.detail_frame.winfo_exists():
                    self.hide_task_details()
                self.root.unbind_all("<Button-1>")
        
        # 绑定点击事件
        self.root.bind_all("<Button-1>", on_click_outside)
        
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
        # 清除当前显示的任务记录
        if hasattr(self, 'current_detail_task'):
            del self.current_detail_task
        
        # 解绑点击事件
        self.root.unbind_all("<Button-1>")

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
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)

    # 添加菜单功能对应的方法
    def toggle_theme(self):
        """切换主题并更新所有组件的颜色"""
        # 切换主题模式
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        
        # 更新颜色方案
        self.colors = self.theme_colors[self.theme_mode]
        
        # 更新 CTk 的外观模式
        ctk.set_appearance_mode(self.theme_mode)
        
        # 更新所有组件颜色
        self.update_theme_colors()
        
        # 更新菜单颜色
        self.update_menu_colors()
        
        # 保存当前主题设置
        self.save_theme_preference()

    def update_theme_colors(self):
        """更新所有组件的颜色"""
        # 更新主窗口
        self.main_frame.configure(fg_color=self.colors["bg"])
        
        # 更新标题栏
        self.title_bar.configure(fg_color=self.colors["titlebar"])
        self.title_label.configure(text_color=self.colors["text"])
        self.min_btn.configure(
            text_color=self.colors["text"],
            hover_color=self.colors["hover"]
        )
        self.close_btn.configure(
            text_color=self.colors["text"],
            hover_color="#FF4757"
        )
        
        # 更新菜单栏
        self.menu_bar.configure(fg_color=self.colors["menubar"])
        
        # 更新侧边栏
        self.sidebar.configure(
            fg_color=self.colors["sidebar"],
            border_color=self.colors["border"]
        )
        
        # 更新类别标题
        self.category_title.configure(text_color=self.colors["text"])
        
        # 更新侧边栏切换按钮
        self.sidebar_toggle_btn.configure(
            text_color=self.colors["text"],
            hover_color=self.colors["hover"]
        )
        
        # 更新任务输入框
        self.task_entry.configure(
            border_color=self.colors["border"],
            fg_color=self.colors["sidebar"],
            text_color=self.colors["text"]
        )
        
        # 更新右侧面板
        self.right_pane.configure(
            fg_color=self.colors["bg"],
            border_color=self.colors["border"]
        )
        
        # 更新任务框架
        self.task_frame.configure(fg_color=self.colors["sidebar"])
        
        # 更新任务滚动区域
        self.task_scroll.configure(fg_color=self.colors["bg"])
        
        # 更新主题按钮
        self.theme_button.configure(
            image=self.theme_icons["light" if self.theme_mode == "light" else "dark"],
            text_color=self.colors["text"],
            border_color=self.colors["border"],
            hover_color=self.colors["hover"]
        )
        
        # 更新类别按钮
        self.update_category_list()
        
        # 更新任务列表
        self.update_task_list()
        
        # 如果有任务详情面板，也需要更新它
        if hasattr(self, 'detail_frame') and self.detail_frame.winfo_exists():
            self.detail_frame.configure(fg_color=self.colors["sidebar"])
            # 更新详情面板中的所有标签和按钮
            for widget in self.detail_frame.winfo_children():
                if isinstance(widget, ctk.CTkLabel):
                    widget.configure(text_color=self.colors["text"])
                elif isinstance(widget, ctk.CTkButton):
                    widget.configure(
                        text_color=self.colors["text"],
                        hover_color=self.colors["hover"]
                    )

    def update_menu_colors(self):
        """更新菜单相关的颜色"""
        # 更新菜单栏背景
        self.menu_bar.configure(fg_color=self.colors["menubar"])
        
        # 更新所有 CustomMenu 实例的颜色
        for widget in self.menu_bar.winfo_children():
            if isinstance(widget, ctk.CTkFrame):  # 菜单容器
                for menu in widget.winfo_children():
                    if isinstance(menu, CustomMenu):
                        menu.update_colors(self.colors)
                        # 更新菜单按钮颜色
                        menu.menu_button.configure(
                            text_color=self.colors["text"],
                            hover_color=self.colors["hover"],
                            fg_color="transparent"
                        )

    def save_theme_preference(self):
        """保存主题设置到数据库"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (?, ?)
            ''', ('theme', self.theme_mode))
            self.conn.commit()
        except Exception as e:
            print(f"Error saving theme: {str(e)}")

    def load_theme_preference(self):
        """从数据库加载主题设置"""
        try:
            self.cursor.execute('SELECT value FROM settings WHERE key = ?', ('theme',))
            result = self.cursor.fetchone()
            self.theme_mode = result[0] if result else 'light'
            self.colors = self.theme_colors[self.theme_mode]
            ctk.set_appearance_mode(self.theme_mode)
        except Exception as e:
            print(f"Error loading theme: {str(e)}")
            self.theme_mode = 'light'
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
            self.show_message("备份失败", f"备份数据时错：{str(e)}")

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
                self.show_message("恢复失败", f"恢复数据时出错：{str(e)}")

    def clear_completed(self):
        # 实现清已成任务功能
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
            "BoBoMaker 智能清单 使用说明：\n\n"
            "1. 左侧边栏显示任务类别\n"
            "2. 可以添加编辑类别\n"
            "3. 在输入框中输入任务按回车添加\n"
            "4. 点击复选框任务完成状态\n"
            "5. 点击任务可查看详细信息\n"
            "6. 使用菜单栏进行更多操作"
        )

    def show_about(self):
        self.show_message("关于", 
            f"BoBoMaker 智能清单  {self.version}\n\n"
            "BoBoMaker 是一个极客项目\n"
            "旨在为大家提供常用软件的开源平替\n"
            "告别广告和收费，享受纯净体验\n\n"
            "项目网站：http://writerpanda.cn\n\n"
            "让我们一起打造更好的软件生态！"
        )

    def show_message(self, title, message):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设置大小并居中
        self.center_window(dialog, 400, 250)
        
        # 如果消息中包含网址，将消息分成多个部分
        if "http://" in message or "https://" in message:
            # 分割消息，找到网址前后的文本
            parts = message.split("http://")
            pre_text = parts[0]
            url_text = "http://" + parts[1].split("\n")[0]
            post_text = "\n".join(parts[1].split("\n")[1:])
            
            # 显示网址前的文本
            if pre_text:
                pre_label = ctk.CTkLabel(
                    dialog,
                    text=pre_text,
                    font=("微软雅黑", 12),
                    wraplength=350,
                    justify="center"
                )
                pre_label.pack(pady=(20, 5))
            
            # 显示网址为可点击的链接
            link_label = ctk.CTkLabel(
                dialog,
                text=url_text,
                font=("微软雅黑", 12),
                text_color="#4A90E2",
                cursor="hand2"
            )
            link_label.pack(pady=5)
            link_label.bind("<Button-1>", lambda e: webbrowser.open(url_text))
            
            # 显示网址后的文本
            if post_text:
                post_label = ctk.CTkLabel(
                    dialog,
                    text=post_text,
                    font=("微软雅黑", 12),
                    wraplength=350,
                    justify="center"
                )
                post_label.pack(pady=(5, 20))
        else:
            # 如果没有网址，直接显示整个消息
            msg_label = ctk.CTkLabel(
                dialog, 
                text=message,
                font=("微软雅黑", 12),
                wraplength=350,
                justify="center"
            )
            msg_label.pack(pady=(20, 20))
        
        # 确定按钮 - 修改样式
        ctk.CTkButton(
            dialog,
            text="确定",
            command=dialog.destroy,
            width=100,  # 增加宽度
            height=55,  # 增加高度
            corner_radius=8,  # 设置圆角
            font=("微软雅黑", 12),  # 设置字体
            hover_color=self.colors["accent"]  # 设置悬停颜色
        ).pack(pady=(0, 20))

    def show_confirm(self, title, message):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 先设大小并居中
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
        menu.add_command(label="分析", 
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
                     text="输入新类名称:",
                     font=("微软雅黑", 12)).pack(pady=(15, 5))
        
        # 创建输入框并预填充当前类别名称
        entry = ctk.CTkEntry(dialog, width=350)
        entry.pack(padx=20, pady=5)
        entry.insert(0, category)  # 预充当前类称
        entry.select_range(0, 'end')  # 选中所有文本
        entry.focus()  # 获取焦点
        
        def save_changes():
            new_name = entry.get().strip()
            if new_name and new_name != category and new_name not in self.categories:
                # 获取所类别的顺序
                categories = list(self.categories.items())
                # 找到当前类别的索引
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
        analysis_window.title(f"类别分析 - {category}")
        
        # 先设置大小居中
        self.center_window(analysis_window, 600, 400)
        
        # 获取任务数据
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
        
        # 按日倒序列
        for date in sorted(date_stats.keys(), reverse=True):
            count = date_stats[date]
            daily_text = f"{date}: 完成 {count} 个任务"
            ctk.CTkLabel(scroll_frame,
                        text=daily_text,
                        font=("微软雅黑", 12),
                        anchor="w").pack(fill="x", pady=2)  # 移除多余的括号
        
        # 如果没有完成记录
        if not date_stats:
            ctk.CTkLabel(scroll_frame,
                        text="暂无完成记录",
                        font=("微软雅黑", 12),
                        text_color="gray").pack(pady=10)  # 移除多余的括号

    # 添加拖拽相关的方
    def on_button_press(self, event, widget, category):
        # 记录开始时间和位置
        self.press_data = {
            "time": event.time,
            "y": event.y_root,
            "widget": widget,
            "category": widget._category_name,
            "start_y": event.y_root  # 记录初始位置
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
            
            # 确定所有按钮都可见
            for btn in self.category_buttons:
                if btn != widget and not btn.winfo_viewable():
                    btn.pack(fill="x", pady=2)
            
            # 在当前位置创建占位
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
            # 清除所有临时占位符
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
        
        # 创建绑定事件的辅助函数
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
        entry.pack(padx=20, pady=5)  # 减小内边距
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
        
        # 加载并显示图标
        try:
            icon_image = Image.open(get_resource_path("logo.png"))
            # 调整图标大小以适应标题栏
            icon_image = icon_image.resize((20, 20))
            
            # 使用 CTkImage 替代 PhotoImage
            self.title_icon = ctk.CTkImage(
                light_image=icon_image,
                dark_image=icon_image,
                size=(20, 20)
            )
            
            # 创建显示图标的标签
            icon_label = ctk.CTkLabel(
                self.title_bar,
                text="",
                image=self.title_icon,
                width=20,
                height=20
            )
            icon_label.pack(side="left", padx=(10, 5))
        except Exception as e:
            print(f"Error loading title bar icon: {str(e)}")
        
        # 图标和标题
        title_text = f"BoBoMaker 智能清单  {self.version}"
        self.title_label = ctk.CTkLabel(self.title_bar,
                          text=title_text,
                          font=("微软雅黑", 12),
                          text_color=self.colors["text"])
        self.title_label.pack(side="left")
        
        # 窗口控制按钮容器
        btn_container = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        btn_container.pack(side="right", padx=5)
        
        # 最小化按钮
        self.min_btn = ctk.CTkButton(btn_container,
                           text="—",
                           width=35,
                           height=25,
                           command=lambda: self.root.iconify(),
                           fg_color="transparent",
                           text_color=self.colors["text"],
                           hover_color=self.colors["hover"])
        self.min_btn.pack(side="left", padx=2)
        
        # 关闭按钮
        self.close_btn = ctk.CTkButton(btn_container,
                     text="×",  # 使用英文字符 x
                     width=35,
                     height=25,
                     command=self.on_closing,
                     fg_color="transparent",
                     text_color=self.colors["text"],
                     hover_color="#FF4757",
                     font=("Arial", 14))  # 使用 Arial 字体
        self.close_btn.pack(side="left", padx=2)
        
        # 绑定拖动事件 - 只需要绑定开始拖动事件
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_label.bind("<Button-1>", self.start_move)

    def start_move(self, event):
        """处理窗口拖动开始"""
        try:
            # 取消所有定时器
            self.cancel_timers()
            
            # 设置拖动状态
            self.is_dragging = True
            
            # 保存拖动开始时的位置
            self.drag_start_y = event.y_root
            
            from ctypes import windll
            # 获取窗口句柄
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            
            # 使用 Windows API 处理拖动
            windll.user32.ReleaseCapture()
            windll.user32.PostMessageW(hwnd, 0xA1, 2, 0)
            
            # 绑定鼠标释放事件
            self.root.bind("<ButtonRelease-1>", self.on_drag_end, add="+")
            
        except Exception as e:
            print(f"Error in start_move: {str(e)}")

    def on_drag_end(self, event):
        """处理拖动结束"""
        try:
            if not self.is_dragging:
                return
            
            # 重置拖动状态
            self.is_dragging = False
            
            # 解绑鼠标释放事件
            self.root.unbind("<ButtonRelease-1>")
            
            # 获取当前窗口位置
            window_y = self.root.winfo_y()
            
            # 如果窗口在顶部区域
            if window_y < 20:
                if not self.is_docked:
                    # 保存原始几何信息
                    self.original_geometry = self.root.geometry()
                    # 设置停靠状态
                    self.is_docked = True
                    # 吸附到顶部
                    x = self.root.winfo_x()
                    self.root.wm_geometry(f"+{x}+0")
                    # 延迟启动自动隐藏
                    self.root.after(500, self.schedule_hide)
                    # 绑定鼠标事件
                    self.root.bind("<Enter>", self.on_mouse_enter)
                    self.root.bind("<Leave>", self.on_mouse_leave)
            else:
                # 如果窗口离开顶部区域且当前是停靠状态
                if self.is_docked:
                    self.undock_window()
                    
        except Exception as e:
            print(f"Error in on_drag_end: {str(e)}")
        finally:
            self.is_dragging = False

    def undock_window(self):
        """取消窗口停靠状态"""
        if not self.is_docked:
            return
        
        self.is_docked = False
        self.cancel_timers()
        
        if self.original_geometry:
            # 从原始几何信息中获取宽度和高度
            try:
                width, height = map(int, self.original_geometry.split('+')[0].split('x'))
                x = self.root.winfo_x()
                y = self.root.winfo_y()
                # 保持当前x位置，使用原始宽度和高度
                self.root.geometry(f"{width}x{height}+{x}+{y}")
            except:
                # 如果解析失败，直接使用原始几何信息
                self.root.geometry(self.original_geometry)
            
            self.original_geometry = None
        
        # 解绑鼠标事件
        self.root.unbind("<Enter>")
        self.root.unbind("<Leave>")

    def check_dock_position(self):
        """检查窗口位置并决定是否停靠"""
        # 如果正在拖动，不进行停靠检查
        if self.is_dragging:
            return
        
        if not hasattr(self, 'checking_position'):
            self.checking_position = False
        
        if self.checking_position:
            return
        
        self.checking_position = True
        try:
            # 获取窗口当前位置
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            
            # 如果窗口靠近顶部（小于20像素）且未停靠
            if y < 20 and not self.is_docked:
                # 保存原始位置和大小
                self.original_geometry = self.root.geometry()
                # 设置停靠标志
                self.is_docked = True
                # 延迟启动自动隐藏
                self.schedule_hide()
        finally:
            self.checking_position = False

    def schedule_hide(self):
        """计划隐藏窗口"""
        if not self.is_docked:
            return
        
        # 取消所有现有定时器
        self.cancel_timers()
        
        # 设置新的隐藏定时器
        self.hide_timer = self.root.after(500, self.hide_window)

    def hide_window(self):
        """隐藏窗口，只留下一小部分"""
        if not self.is_docked:
            return
            
        # 获取当前窗口位置
        x = self.root.winfo_x()
        
        # 保存完整状态的位置和大小
        if not self.original_geometry:
            self.original_geometry = self.root.geometry()
        
        # 使用固定宽度
        self.root.geometry(f"{self.dock_width}x{self.dock_height}+{x}+0")

    def show_window(self):
        """显示完整窗口"""
        if not self.is_docked or not self.original_geometry:
            return
        
        try:
            # 获取当前位置
            current_x = self.root.winfo_x()
            
            # 从原始几何信息中获取宽度和高度
            width, height = map(int, self.original_geometry.split('+')[0].split('x'))
            
            # 使用当前x位置和原始宽度、高度
            self.root.geometry(f"{width}x{height}+{current_x}+0")
            
            # 确保窗口大小不超过屏幕
            screen_width = self.root.winfo_screenwidth()
            if current_x + width > screen_width:
                # 如果窗口超出屏幕右边界，调整x坐标
                new_x = max(0, screen_width - width)
                self.root.geometry(f"{width}x{height}+{new_x}+0")
            
            # 重新绑定鼠标离开事件
            self.root.bind("<Leave>", self.on_mouse_leave)
            
        except Exception as e:
            print(f"Error restoring window: {str(e)}")
            # 如果出错，尝试直接使用原始几何信息
            self.root.geometry(self.original_geometry)

    def on_mouse_enter(self, event):
        """鼠标进入窗口区域"""
        if self.is_docked:
            # 取消任何正在进行的隐藏计时
            self.cancel_timers()
            
            # 如果窗口当前是隐藏状态，则显示
            if self.root.winfo_height() <= self.dock_height + 5:
                self.show_window()

    def on_mouse_leave(self, event):
        """鼠标离开窗口区域"""
        if self.is_docked:
            # 检查鼠标是否真的离开了窗口区域
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            win_x = self.root.winfo_x()
            win_y = self.root.winfo_y()
            win_width = self.root.winfo_width()
            win_height = self.root.winfo_height()
            
            # 添加一点检测余量
            margin = 2
            if not (win_x - margin <= x <= win_x + win_width + margin and 
                    win_y - margin <= y <= win_y + win_height + margin):
                self.schedule_hide()

    def cancel_timers(self):
        """取消所有定时器"""
        for timer_attr in ['hide_timer', 'show_timer']:
            if hasattr(self, timer_attr) and getattr(self, timer_attr):
                self.root.after_cancel(getattr(self, timer_attr))
                setattr(self, timer_attr, None)

    def on_closing(self):
        """处理窗口关闭事件"""
        try:
            self.cancel_timers()  # 确保清理所有定时器
            self.save_tasks()
            if hasattr(self, 'conn'):
                self.conn.close()
            self.root.quit()
        except:
            self.root.quit()

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

    # 添加新方法来处理侧边栏的展开和收起
    def toggle_sidebar(self):
        # 确保所有必要的属性都已初始化
        if not hasattr(self, 'is_animating'):
            self.is_animating = False
        if not hasattr(self, 'sidebar_width'):
            self.sidebar_width = 120
        if not hasattr(self, 'is_expanded'):
            self.is_expanded = True
        if not hasattr(self, 'max_width'):
            self.max_width = 120
        
        if self.is_animating:  # 如果正在动画中，忽略点击
            return
        
        self.is_animating = True
        current_width = self.sidebar.winfo_width()
        
        if self.is_expanded:  # 使用状态标志而不是宽度判断
            # 保存当前宽度用于恢复，但不超过最大宽度
            self.sidebar_width = min(current_width, self.max_width)
            self.is_expanded = False  # 更新状态
            
            # 立即隐藏内容避免拖影
            self.category_title.pack_forget()
            self.category_frame.pack_forget()
            
            # 更新按钮文本并保持在原位
            self.sidebar_toggle_btn.configure(text="▶")
            
            # 开始收起动画
            self.animate_sidebar(current_width, 30, False)
        else:
            self.is_expanded = True  # 更新状态
            # 确保展开宽度在有效范围内
            if self.sidebar_width < 120:
                self.sidebar_width = 120
            elif self.sidebar_width > self.max_width:
                self.sidebar_width = self.max_width
            
            # 开始展开动画前先调整按钮
            self.sidebar_toggle_btn.configure(text="◀")
            self.sidebar_toggle_btn.pack(in_=self.title_bar_frame, side="right", padx=5)
            
            # 开始展开动画
            self.animate_sidebar(30, self.sidebar_width, True)

    def animate_sidebar(self, start_width, end_width, is_expanding):
        """处理侧边栏动画效果"""
        if not hasattr(self, 'animation_id'):
            self.animation_id = None
        
        # 如果有正在进行的动画，取消它
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        
        # 确保结束宽度不超过最大宽度
        if is_expanding:
            end_width = min(end_width, self.max_width)
        
        duration = 200
        steps = 15
        step_time = duration / steps
        width_step = (end_width - start_width) / steps
        
        def update_width(current_step):
            if current_step < steps:
                try:
                    new_width = int(start_width + (width_step * current_step))
                    # 确保新宽度不超过最大宽度
                    new_width = min(new_width, self.max_width)
                    self.sidebar.configure(width=new_width)
                    
                    # 如果是展开动画的最后几步，开始显示内容
                    if is_expanding and current_step > steps * 0.8:
                        if not self.category_title.winfo_ismapped():
                            self.category_title.pack(in_=self.title_bar_frame, side="left", padx=10)
                        if not self.category_frame.winfo_ismapped():
                            self.category_frame.pack(fill="both", expand=True, padx=10)
                    
                    # 保存动画ID以便可以取消
                    self.animation_id = self.root.after(int(step_time), 
                                                          lambda: update_width(current_step + 1))
                except Exception as e:
                    print(f"Animation error: {str(e)}")
                    self.cleanup_animation()
            else:
                try:
                    # 确保最终宽度精确且不超过最大宽度
                    final_width = min(end_width, self.max_width)
                    self.sidebar.configure(width=final_width)
                    
                    # 如果是展开动画，确保内容完全显示
                    if is_expanding:
                        if not self.category_title.winfo_ismapped():
                            self.category_title.pack(in_=self.title_bar_frame, side="left", padx=10)
                        if not self.category_frame.winfo_ismapped():
                            self.category_frame.pack(fill="both", expand=True, padx=10)
                    
                    # 清理动画状态
                    self.cleanup_animation()
                except Exception as e:
                    print(f"Animation completion error: {str(e)}")
                    self.cleanup_animation()
        
        # 开始动画
        update_width(0)

    def cleanup_animation(self):
        """清理动画相关的状态"""
        self.is_animating = False
        if hasattr(self, 'animation_id') and self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None

    def create_menu_bar(self):
        # 创建菜单栏容器
        self.menu_bar = ctk.CTkFrame(
            self.main_frame,
            height=30,
            fg_color=self.colors["sidebar"],
            border_width=0,
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
        
        # 在右侧添加主题切换按钮
        theme_container = ctk.CTkFrame(
            self.menu_bar,
            fg_color="transparent"
        )
        theme_container.pack(side="right", padx=10)
        
        # 主题切换按钮
        self.theme_button = ctk.CTkButton(
            theme_container,
            text="",  # 不使用文本
            image=self.theme_icons["light" if self.theme_mode == "light" else "dark"],
            width=32,
            height=32,
            corner_radius=8,
            fg_color="transparent",
            text_color=self.colors["text"],
            hover_color=self.colors["hover"],
            border_width=1,
            border_color=self.colors["border"],
            command=self.toggle_theme
        )
        self.theme_button.pack(side="right")

if __name__ == "__main__":
    root = ctk.CTk()
    app = TaskManager(root)
    app.center_window(root, 900, 600)
    root.mainloop()