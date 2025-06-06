import accesskit
import os
import platform
import pygame

PLATFORM_SYSTEM = platform.system()

WINDOW_TITLE = "Hello world"
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 200

WINDOW_ID = 0
BUTTON_1_ID = 1
BUTTON_2_ID = 2
ANNOUNCEMENT_ID = 3
INITIAL_FOCUS = BUTTON_1_ID

BUTTON_1_RECT = accesskit.Rect(20.0, 20.0, 100.0, 60.0)

BUTTON_2_RECT = accesskit.Rect(20.0, 60.0, 100.0, 100.0)

ACCESSKIT_EVENT = pygame.event.custom_type()
SET_FOCUS_MSG = 0
DO_DEFAULT_ACTION_MSG = 1


def build_button(id, label):
    node = accesskit.Node(accesskit.Role.BUTTON)
    node.set_bounds(BUTTON_1_RECT if id == BUTTON_1_ID else BUTTON_2_RECT)
    node.set_label(label)
    node.add_action(accesskit.Action.CLICK)
    node.add_action(accesskit.Action.FOCUS)
    return node


def build_announcement(text):
    node = accesskit.Node(accesskit.Role.LABEL)
    node.set_value(text)
    node.set_live(accesskit.Live.POLITE)
    return node


class PygameAdapter:
    def __init__(self, activation_handler, action_handler, deactivation_handler):
        if PLATFORM_SYSTEM == "Darwin":
            accesskit.macos.add_focus_forwarder_to_window_class("SDLWindow")
            window = pygame.display.get_wm_info()["window"]
            self.adapter = accesskit.macos.SubclassingAdapter.for_window(
                window, activation_handler, action_handler
            )
        elif os.name == "posix":
            self.adapter = accesskit.unix.Adapter(
                activation_handler, action_handler, deactivation_handler
            )
        elif PLATFORM_SYSTEM == "Windows":
            hwnd = pygame.display.get_wm_info()["window"]
            self.adapter = accesskit.windows.SubclassingAdapter(
                hwnd, activation_handler, action_handler
            )

    def update_if_active(self, update_factory):
        events = self.adapter.update_if_active(update_factory)
        if events is not None:
            events.raise_events()

    def update_window_focus_state(self, is_focused):
        if PLATFORM_SYSTEM == "Darwin":
            events = self.adapter.update_view_focus_state(is_focused)
            if events is not None:
                events.raise_events()
        elif os.name == "posix":
            self.adapter.update_window_focus_state(is_focused)


class WindowState:
    def __init__(self):
        self.focus = INITIAL_FOCUS
        self.announcement = None

    def build_root(self):
        node = accesskit.Node(accesskit.Role.WINDOW)
        node.set_children([BUTTON_1_ID, BUTTON_2_ID])
        if self.announcement is not None:
            node.push_child(ANNOUNCEMENT_ID)
        node.set_label(WINDOW_TITLE)
        return node

    def build_initial_tree(self):
        root = self.build_root()
        button_1 = build_button(BUTTON_1_ID, "Button 1")
        button_2 = build_button(BUTTON_2_ID, "Button 2")
        result = accesskit.TreeUpdate(self.focus)
        tree = accesskit.Tree(WINDOW_ID)
        tree.app_name = "Hello world"
        result.tree = tree
        result.nodes.append((WINDOW_ID, root))
        result.nodes.append((BUTTON_1_ID, button_1))
        result.nodes.append((BUTTON_2_ID, button_2))
        if self.announcement is not None:
            result.nodes.append(
                (
                    ANNOUNCEMENT_ID,
                    build_announcement(self.announcement),
                )
            )
        return result

    def press_button(self, adapter, id):
        self.announcement = (
            "You pressed button 1" if id == BUTTON_1_ID else "You pressed button 2"
        )
        adapter.update_if_active(self.build_tree_update_for_button_press)

    def build_tree_update_for_button_press(self):
        update = accesskit.TreeUpdate(self.focus)
        update.nodes.append((ANNOUNCEMENT_ID, build_announcement(self.announcement)))
        update.nodes.append((WINDOW_ID, self.build_root()))
        return update

    def set_focus(self, adapter, focus):
        self.focus = focus
        adapter.update_if_active(self.build_tree_update_for_focus_update)

    def build_tree_update_for_focus_update(self):
        return accesskit.TreeUpdate(self.focus)

    def deactivate_accessibility(self):
        # There's nothing in the state that depends on whether the adapter
        # is active, so there's nothing to do here.
        pass


def do_action(request):
    if request.action in [accesskit.Action.CLICK, accesskit.Action.FOCUS]:
        args = {
            "event": SET_FOCUS_MSG
            if request.action == accesskit.Action.FOCUS
            else DO_DEFAULT_ACTION_MSG,
            "target": request.target,
        }
        event = pygame.event.Event(ACCESSKIT_EVENT, args)
        pygame.event.post(event)


def main():
    print("This example has no visible GUI, and a keyboard interface:")
    print("- [Tab] switches focus between two logical buttons.")
    print(
        "- [Space] 'presses' the button, adding static text in a live region announcing that it was pressed."
    )
    if PLATFORM_SYSTEM == "Windows":
        print(
            "Enable Narrator with [Win]+[Ctrl]+[Enter] (or [Win]+[Enter] on older versions of Windows)."
        )
    elif os.name == "posix" and PLATFORM_SYSTEM != "Darwin":
        print("Enable Orca with [Super]+[Alt]+[S].")

    state = WindowState()
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.HIDDEN)
    pygame.display.set_caption(WINDOW_TITLE)
    adapter = PygameAdapter(
        state.build_initial_tree, do_action, state.deactivate_accessibility
    )
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SHOWN)
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.WINDOWFOCUSGAINED:
                adapter.update_window_focus_state(True)
            elif event.type == pygame.WINDOWFOCUSLOST:
                adapter.update_window_focus_state(False)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    new_focus = (
                        BUTTON_2_ID if state.focus == BUTTON_1_ID else BUTTON_1_ID
                    )
                    state.set_focus(adapter, new_focus)
                elif event.key == pygame.K_SPACE:
                    state.press_button(adapter, state.focus)
            elif event.type == ACCESSKIT_EVENT and event.__dict__["target"] in [
                BUTTON_1_ID,
                BUTTON_2_ID,
            ]:
                target = event.__dict__["target"]
                if event.__dict__["event"] == SET_FOCUS_MSG:
                    state.set_focus(adapter, target)
                elif event.__dict__["event"] == DO_DEFAULT_ACTION_MSG:
                    state.press_button(adapter, target)


if __name__ == "__main__":
    main()
