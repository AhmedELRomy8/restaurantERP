"""
Restaurant ERP Mobile App - Kivy Version for Android/iOS
Simplified version optimized for mobile screens
"""
import os
os.environ['TK_LIBRARY'] = '/system/lib'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen, ScreenManager

import database as db
from datetime import datetime

# Set window size for mobile
Window.size = (1080, 1920)  # Full HD Mobile Size

# Color Scheme
COLORS = {
    'primary': (0.06, 0.08, 0.1, 1),        # Dark background
    'secondary': (0.1, 0.12, 0.15, 1),     # Secondary background
    'accent': (1, 0.55, 0.25, 1),          # Orange accent
    'success': (0.3, 0.8, 0.3, 1),         # Green
    'danger': (0.94, 0.33, 0.31, 1),       # Red
    'text_primary': (0.93, 0.93, 0.93, 1), # Light text
    'text_secondary': (0.56, 0.64, 0.68, 1), # Muted text
}


class LoginScreen(Screen):
    """Mobile login screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'login'
        
        layout = BoxLayout(orientation='vertical', padding='20dp', spacing='15dp')
        layout.canvas.before.clear()
        with layout.canvas.before:
            Color(*COLORS['primary'])
            Rectangle(size=Window.size, pos=layout.pos)
        
        # Logo
        logo = Label(text='🍽️ Restaurant ERP', size_hint_y=0.2,
                    color=COLORS['accent'], font_size='28sp', bold=True)
        layout.add_widget(logo)
        
        # Spacer
        layout.add_widget(Label(size_hint_y=0.1))
        
        # Username
        self.username = TextInput(multiline=False, hint_text='Username',
                                   size_hint_y=0.08, background_color=COLORS['secondary'],
                                   foreground_color=COLORS['text_primary'])
        layout.add_widget(self.username)
        
        # Password
        self.password = TextInput(multiline=False, hint_text='Password', password=True,
                                   size_hint_y=0.08, background_color=COLORS['secondary'],
                                   foreground_color=COLORS['text_primary'])
        layout.add_widget(self.password)
        
        # Spacer
        layout.add_widget(Label(size_hint_y=0.2))
        
        # Login Button
        login_btn = Button(text='Login', size_hint_y=0.1,
                          background_color=COLORS['accent'],
                          background_normal='')
        login_btn.bind(on_press=self.login)
        layout.add_widget(login_btn)
        
        self.add_widget(layout)
    
    def login(self, instance):
        username = self.username.text
        password = self.password.text
        
        user = db.authenticate_user(username, password)
        if user:
            app = App.get_running_app()
            app.current_user = user
            self.manager.current = 'dashboard'
        else:
            self.show_error('Invalid credentials')
    
    def show_error(self, msg):
        content = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        content.add_widget(Label(text=msg, size_hint_y=0.8))
        btn = Button(text='OK', size_hint_y=0.2, background_color=COLORS['accent'])
        content.add_widget(btn)
        
        popup = Popup(title='Error', content=content, size_hint=(0.9, 0.3))
        btn.bind(on_press=popup.dismiss)
        popup.open()


class DashboardScreen(Screen):
    """Mobile dashboard showing quick stats and actions"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'dashboard'
        
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        layout.canvas.before.clear()
        with layout.canvas.before:
            Color(*COLORS['primary'])
            Rectangle(size=Window.size, pos=layout.pos)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, padding='10dp')
        header.canvas.before.clear()
        with header.canvas.before:
            Color(*COLORS['secondary'])
            Rectangle(size=header.size, pos=header.pos)
        
        header.add_widget(Label(text='📊 Dashboard', font_size='20sp', bold=True,
                               color=COLORS['text_primary']))
        layout.add_widget(header)
        
        # Quick Stats
        stats = GridLayout(cols=2, size_hint_y=0.25, spacing='8dp', padding='8dp')
        
        for icon, stat, value in [
            ('📦', 'Orders', '12'),
            ('💵', 'Revenue', '2,500'),
            ('🚗', 'Deliveries', '8'),
            ('🪑', 'Tables', '4 of 12'),
        ]:
            card = BoxLayout(orientation='vertical', padding='10dp')
            card.canvas.before.clear()
            with card.canvas.before:
                Color(*COLORS['secondary'])
                Rectangle(size=card.size, pos=card.pos)
            card.add_widget(Label(text=icon, font_size='20sp', size_hint_y=0.4))
            card.add_widget(Label(text=stat, font_size='10sp', color=COLORS['text_secondary']))
            card.add_widget(Label(text=value, font_size='18sp', bold=True,
                                 color=COLORS['accent']))
            stats.add_widget(card)
        
        layout.add_widget(stats)
        
        # Action Buttons
        actions = GridLayout(cols=2, size_hint_y=0.55, spacing='8dp', padding='8dp')
        
        buttons = [
            ('💵 Cashier', 'cashier'),
            ('📦 Orders', 'orders'),
            ('🚗 Delivery', 'delivery'),
            ('🍽️ Menu', 'menu'),
            ('📋 Inventory', 'inventory'),
            ('⚙️ Settings', 'settings'),
        ]
        
        for label, screen in buttons:
            btn = Button(text=label, background_color=COLORS['accent'],
                        background_normal='')
            btn.bind(on_press=lambda x, s=screen: setattr(self.manager, 'current', s))
            actions.add_widget(btn)
        
        layout.add_widget(actions)
        
        self.add_widget(layout)


class CashierScreen(Screen):
    """Mobile cashier / POS screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'cashier'
        
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        layout.canvas.before.clear()
        with layout.canvas.before:
            Color(*COLORS['primary'])
            Rectangle(size=Window.size, pos=layout.pos)
        
        # Header
        header = BoxLayout(size_hint_y=0.08)
        header.canvas.before.clear()
        with header.canvas.before:
            Color(*COLORS['secondary'])
            Rectangle(size=header.size, pos=header.pos)
        
        back_btn = Button(text='← Back', size_hint_x=0.2, background_color=COLORS['accent'])
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='💵 Cashier', font_size='18sp', bold=True,
                               color=COLORS['text_primary']))
        layout.add_widget(header)
        
        # Total Display
        total_layout = BoxLayout(size_hint_y=0.15, padding='10dp')
        total_layout.canvas.before.clear()
        with total_layout.canvas.before:
            Color(*COLORS['secondary'])
            Rectangle(size=total_layout.size, pos=total_layout.pos)
        
        total_layout.add_widget(Label(text='Total', color=COLORS['text_secondary'],
                                      font_size='14sp', size_hint_x=0.5))
        self.total_label = Label(text='0.00 EGP', color=COLORS['accent'],
                                font_size='24sp', bold=True, size_hint_x=0.5)
        total_layout.add_widget(self.total_label)
        layout.add_widget(total_layout)
        
        # Categories & Items (simplified)
        menu_layout = GridLayout(cols=2, size_hint_y=0.6, spacing='8dp', padding='8dp')
        
        categories = db.get_categories()
        for cat in categories[:6]:  # Show first 6 categories
            btn = Button(text=cat.get('icon', '🍽️') + ' ' + cat.get('name', ''),
                        background_color=COLORS['secondary'],
                        background_normal='')
            menu_layout.add_widget(btn)
        
        layout.add_widget(menu_layout)
        
        # Payment Buttons
        payment_layout = GridLayout(cols=2, size_hint_y=0.12, spacing='8dp', padding='8dp')
        
        for method in [('💳 Card', 'card'), ('💵 Cash', 'cash')]:
            btn = Button(text=method[0], background_color=COLORS['success'],
                        background_normal='')
            payment_layout.add_widget(btn)
        
        cancel_btn = Button(text='Cancel', background_color=COLORS['danger'],
                           background_normal='', size_hint_x=0.5)
        payment_layout.add_widget(cancel_btn)
        
        layout.add_widget(payment_layout)
        
        self.add_widget(layout)


class OrdersScreen(Screen):
    """Mobile orders list screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'orders'
        
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        layout.canvas.before.clear()
        with layout.canvas.before:
            Color(*COLORS['primary'])
            Rectangle(size=Window.size, pos=layout.pos)
        
        # Header
        header = BoxLayout(size_hint_y=0.08)
        header.canvas.before.clear()
        with header.canvas.before:
            Color(*COLORS['secondary'])
            Rectangle(size=header.size, pos=header.pos)
        
        back_btn = Button(text='← Back', size_hint_x=0.2, background_color=COLORS['accent'])
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='📦 Orders', font_size='18sp', bold=True,
                               color=COLORS['text_primary']))
        layout.add_widget(header)
        
        # Orders List
        scroll = ScrollView(size_hint_y=0.92)
        orders_list = GridLayout(cols=1, spacing='10dp', padding='8dp',
                                size_hint_y=None)
        orders_list.bind(minimum_height=orders_list.setter('height'))
        
        orders = db.get_all_orders(limit=10)
        for order in orders:
            order_item = BoxLayout(orientation='vertical', size_hint_y=None,
                                  height='60dp', padding='8dp', spacing='4dp')
            order_item.canvas.before.clear()
            with order_item.canvas.before:
                Color(*COLORS['secondary'])
                Rectangle(size=order_item.size, pos=order_item.pos)
            
            order_item.add_widget(Label(
                text=f"{order.get('order_number')} - {order.get('customer_name', 'Walk-in')}",
                font_size='14sp', bold=True, color=COLORS['text_primary'],
                size_hint_y=0.5
            ))
            order_item.add_widget(Label(
                text=f"{order.get('total', 0):.2f} EGP | {order.get('status', 'unknown')}",
                font_size='12sp', color=COLORS['accent'], size_hint_y=0.5
            ))
            
            orders_list.add_widget(order_item)
        
        scroll.add_widget(orders_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)


class DeliveryScreen(Screen):
    """Mobile delivery management screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'delivery'
        
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        layout.canvas.before.clear()
        with layout.canvas.before:
            Color(*COLORS['primary'])
            Rectangle(size=Window.size, pos=layout.pos)
        
        # Header
        header = BoxLayout(size_hint_y=0.08)
        header.canvas.before.clear()
        with header.canvas.before:
            Color(*COLORS['secondary'])
            Rectangle(size=header.size, pos=header.pos)
        
        back_btn = Button(text='← Back', size_hint_x=0.2, background_color=COLORS['accent'])
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='🚗 Deliveries', font_size='18sp', bold=True,
                               color=COLORS['text_primary']))
        layout.add_widget(header)
        
        # Status Tabs
        tabs = GridLayout(cols=3, size_hint_y=0.08, spacing='4dp', padding='4dp')
        for status in ['Pending', 'In Transit', 'Delivered']:
            btn = Button(text=status, background_color=COLORS['secondary'],
                        background_normal='')
            tabs.add_widget(btn)
        layout.add_widget(tabs)
        
        # Deliveries List
        scroll = ScrollView(size_hint_y=0.84)
        deliveries_list = GridLayout(cols=1, spacing='10dp', padding='8dp',
                                    size_hint_y=None)
        deliveries_list.bind(minimum_height=deliveries_list.setter('height'))
        
        deliveries = db.get_all_deliveries(limit=10)
        for delivery in deliveries:
            delivery_item = BoxLayout(orientation='vertical', size_hint_y=None,
                                     height='80dp', padding='8dp', spacing='4dp')
            delivery_item.canvas.before.clear()
            with delivery_item.canvas.before:
                Color(*COLORS['secondary'])
                Rectangle(size=delivery_item.size, pos=delivery_item.pos)
            
            delivery_item.add_widget(Label(
                text=f"Order: {delivery.get('order_number')}",
                font_size='14sp', bold=True, color=COLORS['text_primary'],
                size_hint_y=0.3
            ))
            delivery_item.add_widget(Label(
                text=f"Driver: {delivery.get('delivery_person', 'N/A')}",
                font_size='12sp', color=COLORS['text_secondary'], size_hint_y=0.2
            ))
            delivery_item.add_widget(Label(
                text=f"Address: {delivery.get('delivery_address', '')[:40]}...",
                font_size='11sp', color=COLORS['text_secondary'], size_hint_y=0.2
            ))
            delivery_item.add_widget(Label(
                text=f"Status: {delivery.get('status', 'unknown')}",
                font_size='12sp', color=COLORS['accent'], bold=True, size_hint_y=0.3
            ))
            
            deliveries_list.add_widget(delivery_item)
        
        scroll.add_widget(deliveries_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)


class MenuScreen(Screen):
    """Mobile menu browsing screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'menu'
        
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        layout.canvas.before.clear()
        with layout.canvas.before:
            Color(*COLORS['primary'])
            Rectangle(size=Window.size, pos=layout.pos)
        
        # Header
        header = BoxLayout(size_hint_y=0.08)
        header.canvas.before.clear()
        with header.canvas.before:
            Color(*COLORS['secondary'])
            Rectangle(size=header.size, pos=header.pos)
        
        back_btn = Button(text='← Back', size_hint_x=0.2, background_color=COLORS['accent'])
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='🍽️ Menu', font_size='18sp', bold=True,
                               color=COLORS['text_primary']))
        layout.add_widget(header)
        
        # Menu Items
        scroll = ScrollView(size_hint_y=0.92)
        menu_list = GridLayout(cols=1, spacing='10dp', padding='8dp',
                              size_hint_y=None)
        menu_list.bind(minimum_height=menu_list.setter('height'))
        
        items = db.get_menu_items(limit=15)
        for item in items:
            menu_item = BoxLayout(orientation='vertical', size_hint_y=None,
                                 height='70dp', padding='8dp', spacing='4dp')
            menu_item.canvas.before.clear()
            with menu_item.canvas.before:
                Color(*COLORS['secondary'])
                Rectangle(size=menu_item.size, pos=menu_item.pos)
            
            menu_item.add_widget(Label(
                text=item.get('name', ''),
                font_size='14sp', bold=True, color=COLORS['text_primary'],
                size_hint_y=0.4
            ))
            menu_item.add_widget(Label(
                text=f"{item.get('description', '')[:40]}...",
                font_size='11sp', color=COLORS['text_secondary'], size_hint_y=0.3
            ))
            menu_item.add_widget(Label(
                text=f"{item.get('price', 0):.2f} EGP",
                font_size='13sp', bold=True, color=COLORS['accent'], size_hint_y=0.3
            ))
            
            menu_list.add_widget(menu_item)
        
        scroll.add_widget(menu_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)


class InventoryScreen(Screen):
    """Mobile inventory management screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'inventory'
        
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        layout.canvas.before.clear()
        with layout.canvas.before:
            Color(*COLORS['primary'])
            Rectangle(size=Window.size, pos=layout.pos)
        
        # Header
        header = BoxLayout(size_hint_y=0.08)
        header.canvas.before.clear()
        with header.canvas.before:
            Color(*COLORS['secondary'])
            Rectangle(size=header.size, pos=header.pos)
        
        back_btn = Button(text='← Back', size_hint_x=0.2, background_color=COLORS['accent'])
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='📋 Inventory', font_size='18sp', bold=True,
                               color=COLORS['text_primary']))
        layout.add_widget(header)
        
        # Inventory Items
        scroll = ScrollView(size_hint_y=0.92)
        inventory_list = GridLayout(cols=1, spacing='10dp', padding='8dp',
                                   size_hint_y=None)
        inventory_list.bind(minimum_height=inventory_list.setter('height'))
        
        items = db.get_inventory()
        for item in items[:20]:
            inv_item = BoxLayout(orientation='vertical', size_hint_y=None,
                                height='70dp', padding='8dp', spacing='4dp')
            inv_item.canvas.before.clear()
            with inv_item.canvas.before:
                Color(*COLORS['secondary'])
                Rectangle(size=inv_item.size, pos=inv_item.pos)
            
            status_color = COLORS['success'] if item.get('quantity', 0) > item.get('min_quantity', 0) else COLORS['danger']
            
            inv_item.add_widget(Label(
                text=item.get('name', ''),
                font_size='14sp', bold=True, color=COLORS['text_primary'],
                size_hint_y=0.4
            ))
            inv_item.add_widget(Label(
                text=f"Stock: {item.get('quantity', 0):.1f} {item.get('unit', 'unit')}",
                font_size='12sp', color=status_color, bold=True, size_hint_y=0.3
            ))
            inv_item.add_widget(Label(
                text=f"Min: {item.get('min_quantity', 0):.1f} | Cost: {item.get('cost_per_unit', 0):.2f} EGP/unit",
                font_size='11sp', color=COLORS['text_secondary'], size_hint_y=0.3
            ))
            
            inventory_list.add_widget(inv_item)
        
        scroll.add_widget(inventory_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)


class SettingsScreen(Screen):
    """Mobile settings screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        
        layout = BoxLayout(orientation='vertical', padding='10dp', spacing='10dp')
        layout.canvas.before.clear()
        with layout.canvas.before:
            Color(*COLORS['primary'])
            Rectangle(size=Window.size, pos=layout.pos)
        
        # Header
        header = BoxLayout(size_hint_y=0.08)
        header.canvas.before.clear()
        with header.canvas.before:
            Color(*COLORS['secondary'])
            Rectangle(size=header.size, pos=header.pos)
        
        back_btn = Button(text='← Back', size_hint_x=0.2, background_color=COLORS['accent'])
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'dashboard'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='⚙️ Settings', font_size='18sp', bold=True,
                               color=COLORS['text_primary']))
        layout.add_widget(header)
        
        # Settings Options
        options = GridLayout(cols=1, size_hint_y=0.8, spacing='10dp', padding='10dp')
        
        settings = [
            ('👤 Profile', 'profile'),
            ('🔒 Change Password', 'password'),
            ('🌐 App Version', 'version'),
            ('ℹ️ About', 'about'),
            ('🚪 Logout', 'logout'),
        ]
        
        for label, action in settings:
            btn = Button(text=label, background_color=COLORS['secondary'],
                        background_normal='')
            options.add_widget(btn)
        
        layout.add_widget(options)
        
        # Version info
        version_label = Label(text='v1.0.0 | Restaurant ERP Mobile', 
                             size_hint_y=0.1,
                             color=COLORS['text_muted'], font_size='10sp')
        layout.add_widget(version_label)
        
        self.add_widget(layout)


class RestaurantERPMobile(App):
    """Main Kivy application"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        db.init_database()
    
    def build(self):
        # Create screen manager
        manager = ScreenManager()
        
        # Add all screens
        manager.add_widget(LoginScreen(name='login'))
        manager.add_widget(DashboardScreen(name='dashboard'))
        manager.add_widget(CashierScreen(name='cashier'))
        manager.add_widget(OrdersScreen(name='orders'))
        manager.add_widget(DeliveryScreen(name='delivery'))
        manager.add_widget(MenuScreen(name='menu'))
        manager.add_widget(InventoryScreen(name='inventory'))
        manager.add_widget(SettingsScreen(name='settings'))
        
        # Start with login
        manager.current = 'login'
        
        return manager


if __name__ == '__main__':
    app = RestaurantERPMobile()
    app.title = 'Restaurant ERP'
    app.run()
