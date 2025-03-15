#!/usr/bin/env python3

import gi, json
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('WebKit', '6.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Adw, WebKit, Gio, GLib, Pango, PangoCairo, Gdk

class Wiziwig(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.github.fastrizwaan.wiziwig")
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        win = EditorWindow(application=self)
        win.present()

class EditorWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.set_title("HTML Editor")
        self.set_title("Wiziwig")
        self.set_default_size(1000, 700)
        self.add_css_styles()
        self.connect("close-request", self.on_close_request)
        self.initial_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: sans-serif; font-size: 11pt; margin: 20px; line-height: 1.5; }
        @media (prefers-color-scheme: dark) { body { background-color: #121212; color: #e0e0e0; } }
        @media (prefers-color-scheme: light) { body { background-color: #ffffff; color: #000000; } }
        img { max-width: 100%; resize: both; }
    </style>
</head>
<body><p><br></p></body>
</html>"""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(box)
        header = Adw.HeaderBar()
        box.append(header)
        # Toolbar1: File & edit actions
        toolbar1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, margin_top=6, margin_bottom=6)
        box.append(toolbar1)
        # Toolbar2: Formatting & styling (below toolbar1)
        toolbar2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, margin_top=6, margin_bottom=6)
        toolbar2.set_halign(Gtk.Align.START)
        box.append(toolbar2)
        scroll = Gtk.ScrolledWindow(vexpand=True)
        box.append(scroll)
        self.webview = WebKit.WebView(editable=True)
        self.webview.connect('load-changed', self.on_webview_load)
        scroll.set_child(self.webview)
        self.webview.load_html(self.initial_html, "file:///")
        # --- Toolbar1 Buttons ---
        for (icon, handler) in [
            ("document-new", self.on_new_clicked),
            ("document-open", self.on_open_clicked),
            ("document-save", self.on_save_clicked),
            ("document-save-as", self.on_save_as_clicked),
            ("document-print", self.on_print_clicked),
            ("edit-cut", self.on_cut_clicked),
            ("edit-copy", self.on_copy_clicked),
            ("edit-paste", self.on_paste_clicked),
            ("edit-undo", self.on_undo_clicked),
            ("edit-redo", self.on_redo_clicked),
            ("edit-find", self.on_find_clicked),
            ("edit-find-replace", self.on_replace_clicked)
        ]:
            btn = Gtk.Button(icon_name=icon)
            btn.connect("clicked", handler)
            toolbar1.append(btn)
        zoom_store = Gtk.StringList()
        for level in ["10%", "25%", "50%", "75%", "100%", "150%", "200%", "400%", "1000%"]:
            zoom_store.append(level)
        zoom_dropdown = Gtk.DropDown(model=zoom_store)
        zoom_dropdown.set_selected(4)
        zoom_dropdown.connect("notify::selected", self.on_zoom_changed)
        toolbar1.append(zoom_dropdown)
        # --- Toolbar2 Buttons ---
        heading_store = Gtk.StringList()
        for h in ["Normal", "H1", "H2", "H3", "H4", "H5", "H6"]:
            heading_store.append(h)
        heading_dropdown = Gtk.DropDown(model=heading_store)
        heading_dropdown.connect("notify::selected", self.on_heading_changed)
        toolbar2.append(heading_dropdown)
        # Font dropdown
        font_map = PangoCairo.FontMap.get_default()
        families = font_map.list_families()
        font_names = sorted([family.get_name() for family in families])
        font_store = Gtk.StringList()
        for name in font_names:
            font_store.append(name)
        self.font_dropdown = Gtk.DropDown(model=font_store)
        self.font_dropdown.connect("notify::selected", self.on_font_family_changed)
        default_index = font_names.index("Sans") if "Sans" in font_names else 0
        self.font_dropdown.set_selected(default_index)
        toolbar2.append(self.font_dropdown)
        # Size dropdown
        size_store = Gtk.StringList()
        for size in ["8", "10", "11", "12", "14", "16", "18", "24", "36", "48"]:
            size_store.append(size)
        self.size_dropdown = Gtk.DropDown(model=size_store)
        self.size_dropdown.set_selected(2)
        self.size_dropdown.connect("notify::selected", self.on_font_size_changed)
        toolbar2.append(self.size_dropdown)
        # Formatting buttons
        for (icon, handler) in [
            ("format-text-bold-symbolic", self.on_bold_clicked),
            ("format-text-italic-symbolic", self.on_italic_clicked),
            ("format-text-underline-symbolic", self.on_underline_clicked),
            ("format-text-strikethrough-symbolic", self.on_strikethrough_clicked)
        ]:
            btn = Gtk.Button(icon_name=icon)
            btn.connect("clicked", handler)
            toolbar2.append(btn)
        # Alignment buttons
        for (icon, handler) in [
            ("format-justify-left-symbolic", self.on_align_left),
            ("format-justify-center-symbolic", self.on_align_center),
            ("format-justify-right-symbolic", self.on_align_right),
            ("format-justify-fill-symbolic", self.on_align_justify)
        ]:
            btn = Gtk.Button(icon_name=icon)
            btn.connect("clicked", handler)
            toolbar2.append(btn)
        # List buttons
        for (icon, handler) in [
            ("view-list-bullet-symbolic", self.on_bullet_list),
            ("view-list-ordered-symbolic", self.on_number_list)
        ]:
            btn = Gtk.Button(icon_name=icon)
            btn.connect("clicked", handler)
            toolbar2.append(btn)
        # Indent buttons
        for (icon, handler) in [
            ("format-indent-more-symbolic", self.on_indent_more),
            ("format-indent-less-symbolic", self.on_indent_less)
        ]:
            btn = Gtk.Button(icon_name=icon)
            btn.connect("clicked", handler)
            toolbar2.append(btn)
        # Color buttons
        text_color_btn = Gtk.ColorButton()
        text_color_btn.set_title("Text Color")
        text_color_btn.connect("color-set", self.on_text_color_set)
        toolbar2.append(text_color_btn)
        bg_color_btn = Gtk.ColorButton()
        bg_color_btn.set_title("Background Color")
        bg_color_btn.connect("color-set", self.on_bg_color_set)
        toolbar2.append(bg_color_btn)

    def on_webview_load(self, webview, load_event):
        if load_event == WebKit.LoadEvent.FINISHED:
            script = """
                let p = document.querySelector('p');
                if (p) {
                    let range = document.createRange();
                    range.setStart(p, 0);
                    range.setEnd(p, 0);
                    let sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(range);
                }
            """
            self.webview.evaluate_javascript(script, -1, None, None, None, None, None)
            GLib.idle_add(self.webview.grab_focus)

    def exec_js(self, script):
        self.webview.evaluate_javascript(script, -1, None, None, None, None, None)
        self.webview.grab_focus()

    # --- Toolbar1 Handlers ---
    def on_new_clicked(self, btn):
        self.webview.load_html(self.initial_html, "file:///")
    def on_open_clicked(self, btn):
        self.open_file_dialog()
    def on_save_clicked(self, btn):
        dialog = Gtk.FileDialog()
        dialog.set_title("Save HTML File")
        dialog.set_initial_name("document.html")
        filter_html = Gtk.FileFilter()
        filter_html.set_name("HTML Files (*.html)")
        filter_html.add_pattern("*.html")
        filter_store = Gio.ListStore.new(Gtk.FileFilter)
        filter_store.append(filter_html)
        dialog.set_filters(filter_store)
        dialog.save(self, None, self.save_callback)
    def on_save_as_clicked(self, btn):
        self.on_save_clicked(btn)
    def on_print_clicked(self, btn):
        print_operation = WebKit.PrintOperation.new(self.webview)
        print_operation.run_dialog(self)
    def on_cut_clicked(self, btn):
        self.exec_js("document.execCommand('cut')")
    def on_copy_clicked(self, btn):
        self.exec_js("document.execCommand('copy')")
    def on_paste_clicked(self, btn):
        clipboard = Gdk.Display.get_default().get_clipboard()
        clipboard.read_text_async(None, self.on_text_received, None)  # Added None for cancellable and user_data

    def on_text_received(self, clipboard, result, user_data):
        try:
            text = clipboard.read_text_finish(result)
            if text:
                text_json = json.dumps(text)
                self.exec_js(f"document.execCommand('insertText', false, {text_json})")
        except GLib.Error as e:
            print("Paste error:", e.message)

    def on_undo_clicked(self, btn):
        self.exec_js("document.execCommand('undo')")
    def on_redo_clicked(self, btn):
        self.exec_js("document.execCommand('redo')")


    def on_find_clicked(self, btn):
        window = Gtk.Dialog(title="Find", transient_for=self, modal=True)
        content_area = window.get_content_area()
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_area.append(content)
        
        entry = Gtk.Entry(placeholder_text="Enter search term")
        content.append(entry)
        
        window.add_button("Cancel", Gtk.ResponseType.CANCEL)
        find_btn = window.add_button("Find", Gtk.ResponseType.OK)
        find_btn.get_style_context().add_class("suggested-action")
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                search_term = entry.get_text()
                if search_term:
                    script = f"""
                        (function() {{
                            let search = {json.dumps(search_term)};
                            let regex = new RegExp(search, 'gi');
                            document.body.innerHTML = document.body.innerHTML.replace(regex, match => `<span style="background-color: yellow;">${{match}}</span>`);
                        }})();
                    """
                    self.exec_js(script)
            dialog.destroy()
        
        window.connect("response", on_response)
        window.present()

    def on_replace_clicked(self, btn):
        window = Gtk.Dialog(title="Replace", transient_for=self, modal=True)
        content_area = window.get_content_area()
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)
        
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content_area.append(content)
        
        search_entry = Gtk.Entry(placeholder_text="Search term")
        replace_entry = Gtk.Entry(placeholder_text="Replace with")
        content.append(search_entry)
        content.append(replace_entry)
        
        window.add_button("Cancel", Gtk.ResponseType.CANCEL)
        replace_btn = window.add_button("Replace All", Gtk.ResponseType.OK)
        replace_btn.get_style_context().add_class("suggested-action")
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.OK:
                search = search_entry.get_text()
                replacement = replace_entry.get_text()
                if search and replacement:
                    script = f"""
                        (function() {{
                            let search = {json.dumps(search)};
                            let replace = {json.dumps(replacement)};
                            let regex = new RegExp(search, 'gi');
                            document.body.innerHTML = document.body.innerHTML.replace(regex, replace);
                        }})();
                    """
                    self.exec_js(script)
            dialog.destroy()
        
        window.connect("response", on_response)
        window.present()

    def replace_text(self, search, replacement):
        script = f"""document.body.innerHTML = document.body.innerHTML.split({json.dumps(search)}).join({json.dumps(replacement)});"""
        self.exec_js(script)
    def on_zoom_changed(self, dropdown, *args):
        selected_item = dropdown.get_selected_item()
        if selected_item:
            try:
                zoom_level = int(selected_item.get_string().rstrip('%')) / 100.0
                self.webview.set_zoom_level(zoom_level)
            except ValueError:
                pass
    # --- Toolbar2 Handlers ---
    def on_bold_clicked(self, *args):
        self.exec_js("document.execCommand('bold')")
    def on_italic_clicked(self, *args):
        self.exec_js("document.execCommand('italic')")
    def on_underline_clicked(self, *args):
        self.exec_js("document.execCommand('underline')")
    def on_strikethrough_clicked(self, *args):
        self.exec_js("document.execCommand('strikethrough')")
    def on_heading_changed(self, dropdown, *args):
        headings = ["div", "h1", "h2", "h3", "h4", "h5", "h6"]
        selected = dropdown.get_selected()
        if 0 <= selected < len(headings):
            self.exec_js(f"document.execCommand('formatBlock', false, '{headings[selected]}')")
    def on_align_left(self, *args):
        self.exec_js("document.execCommand('justifyLeft')")
    def on_align_center(self, *args):
        self.exec_js("document.execCommand('justifyCenter')")
    def on_align_right(self, *args):
        self.exec_js("document.execCommand('justifyRight')")
    def on_align_justify(self, *args):
        self.exec_js("document.execCommand('justifyFull')")
    def on_bullet_list(self, *args):
        self.exec_js("document.execCommand('insertUnorderedList')")
    def on_number_list(self, *args):
        self.exec_js("document.execCommand('insertOrderedList')")
    def on_indent_more(self, *args):
        self.exec_js("document.execCommand('indent')")
    def on_indent_less(self, *args):
        self.exec_js("document.execCommand('outdent')")

    def on_font_family_changed(self, dropdown, *args):
        if item := dropdown.get_selected_item():
            font_family = item.get_string()
            script = """
                (function() {
                    console.log('Changing font family to: """ + font_family + """');
                    let selection = window.getSelection();
                    if (!selection.rangeCount) {
                        console.log('No selection');
                        return;
                    }
                    let range = selection.getRangeAt(0);
                    console.log('Selected text: ' + range.toString());
                    
                    // Get the common ancestor and check for existing spans
                    let ancestor = range.commonAncestorContainer;
                    let spans = (ancestor.nodeType === 1) 
                        ? ancestor.querySelectorAll('span[style*="font-family"]') 
                        : ancestor.parentElement.querySelectorAll('span[style*="font-family"]');
                    
                    if (spans.length > 0 && range.toString().length > 0) {
                        // Update existing spans within the selection
                        let updated = false;
                        spans.forEach(span => {
                            if (range.intersectsNode(span)) {
                                console.log('Updating existing span: ' + span.outerHTML);
                                span.style.fontFamily = '""" + font_family + """';
                                updated = true;
                            }
                        });
                        if (updated) {
                            // Restore selection
                            let newRange = document.createRange();
                            newRange.setStart(range.startContainer, range.startOffset);
                            newRange.setEnd(range.endContainer, range.endOffset);
                            selection.removeAllRanges();
                            selection.addRange(newRange);
                            console.log('Updated existing spans');
                            return;
                        }
                    }
                    
                    // If no suitable spans, create a new one
                    let contents = range.extractContents();
                    if (!contents.hasChildNodes()) {
                        console.log('No content extracted');
                        range.insertNode(contents);
                        return;
                    }
                    
                    let span = document.createElement('span');
                    span.style.fontFamily = '""" + font_family + """';
                    span.appendChild(contents);
                    
                    range.insertNode(span);
                    console.log('New span created: ' + span.outerHTML);
                    
                    // Restore selection
                    let newRange = document.createRange();
                    newRange.selectNodeContents(span);
                    selection.removeAllRanges();
                    selection.addRange(newRange);
                    console.log('Selection restored');
                })();
            """
            self.exec_js(script)
            
    def on_font_size_changed(self, dropdown, *args):
        if item := dropdown.get_selected_item():
            size_pt = item.get_string()
            script = """
                (function() {
                    let selection = window.getSelection();
                    if (!selection.rangeCount) return;
                    let range = selection.getRangeAt(0);
                    let fragment = range.cloneContents();
                    let tempDiv = document.createElement('div');
                    tempDiv.appendChild(fragment);
                    let content = range.extractContents();
                    let span = document.createElement('span');
                    span.style.fontSize = '""" + size_pt + """pt';
                    let tempElement = document.createElement('div');
                    tempElement.appendChild(content);
                    let fontSizeSpans = tempElement.querySelectorAll('span[style*="font-size"]');
                    for (let oldSpan of fontSizeSpans) {
                        while (oldSpan.firstChild) {
                            oldSpan.parentNode.insertBefore(oldSpan.firstChild, oldSpan);
                        }
                        oldSpan.parentNode.removeChild(oldSpan);
                    }
                    while (tempElement.firstChild) {
                        span.appendChild(tempElement.firstChild);
                    }
                    range.insertNode(span);
                    selection.removeAllRanges();
                    let newRange = document.createRange();
                    newRange.selectNodeContents(span);
                    selection.addRange(newRange);
                })();
            """
            self.exec_js(script)
            
    def on_text_color_set(self, btn):
        color = btn.get_rgba().to_string()
        self.exec_js(f"document.execCommand('foreColor', false, '{color}')")
    def on_bg_color_set(self, btn):
        color = btn.get_rgba().to_string()
        self.exec_js(f"document.execCommand('backColor', false, '{color}')")
    # --- File Handling ---
    def open_file_dialog(self):
        file_dialog = Gtk.FileDialog.new()
        filter_model = Gio.ListStore.new(Gtk.FileFilter)
        filter_model.append(self.create_file_filter())
        file_dialog.set_filters(filter_model)
        file_dialog.open(self, None, self.on_open_file_dialog_response)
    def create_file_filter(self):
        file_filter = Gtk.FileFilter()
        file_filter.set_name("HTML Files (*.html, *.htm)")
        file_filter.add_pattern("*.html")
        file_filter.add_pattern("*.htm")
        return file_filter
    def on_open_file_dialog_response(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file:
                file.load_contents_async(None, self.load_callback)
        except GLib.Error as e:
            print("Open error:", e.message)
    def load_callback(self, file, result):
        try:
            ok, content, _ = file.load_contents_finish(result)
            if ok:
                self.webview.load_html(content.decode(), file.get_uri())
        except GLib.Error as e:
            print("Load error:", e.message)
    def save_callback(self, dialog, result):
        try:
            file = dialog.save_finish(result)
            self.webview.evaluate_javascript("document.documentElement.outerHTML", -1, None, None, None, self.save_html_callback, file)
        except GLib.Error as e:
            print("Save error:", e.message)
    def save_html_callback(self, webview, result, file):
        try:
            js_value = webview.evaluate_javascript_finish(result)
            if js_value:
                html = js_value.to_string()
                file.replace_contents_bytes_async(GLib.Bytes.new(html.encode()), None, False, Gio.FileCreateFlags.REPLACE_DESTINATION, None, self.final_save_callback)
        except GLib.Error as e:
            print("HTML save error:", e.message)
    def final_save_callback(self, file, result):
        try:
            file.replace_contents_finish(result)
            print("File saved successfully to", file.get_path())
        except GLib.Error as e:
            print("Final save error:", e.message)
    def add_css_styles(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b"window { background-color: @window_bg_color; }")
        Gtk.StyleContext.add_provider_for_display(self.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    def on_close_request(self, *args):
        self.get_application().quit()
        return False

if __name__ == "__main__":
    app = Wiziwig()
    app.run()
