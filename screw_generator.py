import math

import FreeCAD as App
import FreeCADGui as Gui
import Part

try:
    from PySide import QtGui
except ImportError:
    from PySide2 import QtWidgets

    class _QtGuiShim(object):
        QDialog = QtWidgets.QDialog
        QFormLayout = QtWidgets.QFormLayout
        QComboBox = QtWidgets.QComboBox
        QDoubleSpinBox = QtWidgets.QDoubleSpinBox
        QDialogButtonBox = QtWidgets.QDialogButtonBox

    QtGui = _QtGuiShim()


PRESETS = {
    "Custom": {
        "diameter": 3.0,
        "length": 16.0,
        "head_width": 5.5,
        "head_length": 2.0,
        "thread_pitch": 0.5,
        "thread_depth": 0.3,
        "thread_angle": 60.0,
        "tolerance": 0.0,
        "thread_type": "Metric ISO",
        "head_type": "Hex",
    },
    "M2": {
        "diameter": 2.0,
        "length": 10.0,
        "head_width": 4.0,
        "head_length": 1.5,
        "thread_pitch": 0.4,
        "thread_depth": 0.24,
        "thread_angle": 60.0,
        "tolerance": 0.0,
        "thread_type": "Metric ISO",
        "head_type": "Hex",
    },
    "M3": {
        "diameter": 3.0,
        "length": 16.0,
        "head_width": 5.5,
        "head_length": 2.0,
        "thread_pitch": 0.5,
        "thread_depth": 0.31,
        "thread_angle": 60.0,
        "tolerance": 0.0,
        "thread_type": "Metric ISO",
        "head_type": "Hex",
    },
    "M4": {
        "diameter": 4.0,
        "length": 20.0,
        "head_width": 7.0,
        "head_length": 2.8,
        "thread_pitch": 0.7,
        "thread_depth": 0.43,
        "thread_angle": 60.0,
        "tolerance": 0.0,
        "thread_type": "Metric ISO",
        "head_type": "Hex",
    },
}


def _safe_float(value, fallback):
    try:
        return float(value)
    except Exception:
        return fallback


def _make_hex_head(width, height):
    radius = width / math.sqrt(3.0)
    points = []
    for i in range(6):
        angle = math.radians(60 * i)
        points.append(App.Vector(radius * math.cos(angle), radius * math.sin(angle), 0))
    points.append(points[0])
    poly = Part.makePolygon(points)
    wire = Part.Wire(poly.Edges)
    face = Part.Face(wire)
    return face.extrude(App.Vector(0, 0, height))


def _make_phillips_head(width, height):
    head = Part.makeCylinder(width / 2.0, height)
    slot_w = max(width * 0.18, 0.4)
    slot_l = width * 0.85
    cut_d = height * 0.45

    slot1 = Part.makeBox(slot_l, slot_w, cut_d)
    slot1.translate(App.Vector(-slot_l / 2.0, -slot_w / 2.0, height - cut_d))

    slot2 = Part.makeBox(slot_w, slot_l, cut_d)
    slot2.translate(App.Vector(-slot_w / 2.0, -slot_l / 2.0, height - cut_d))

    return head.cut(slot1.fuse(slot2))


def _make_socket_cap_head(width, height):
    head = Part.makeCylinder(width / 2.0, height)
    socket_width = width * 0.45
    socket_depth = height * 0.6

    socket = _make_hex_head(socket_width, socket_depth)
    socket.translate(App.Vector(0, 0, height - socket_depth))
    return head.cut(socket)


def _make_pan_head(width, height):
    return Part.makeCylinder(width / 2.0, height)


def _make_flat_head(width, height):
    r = width / 2.0
    top_r = max(r * 0.15, 0.2)
    profile = [
        App.Vector(r, 0, 0),
        App.Vector(top_r, 0, height),
        App.Vector(0, 0, height),
        App.Vector(0, 0, 0),
        App.Vector(r, 0, 0),
    ]
    wire = Part.Wire(Part.makePolygon(profile).Edges)
    face = Part.Face(wire)
    return face.revolve(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 360)


def _build_thread(major_diam, pitch, depth, angle_deg, length):
    root_diam = max(major_diam - 2.0 * depth, major_diam * 0.5)
    root_radius = root_diam / 2.0
    crest_radius = major_diam / 2.0

    flank_half = max((pitch / 2.0) * 0.45, 0.05)
    ang_factor = max(math.tan(math.radians(max(angle_deg, 1.0) / 2.0)), 0.01)
    crest_shift = min(depth / ang_factor, flank_half)

    p1 = App.Vector(root_radius, 0, -flank_half)
    p2 = App.Vector(root_radius, 0, flank_half)
    p3 = App.Vector(crest_radius, 0, crest_shift)
    p4 = App.Vector(crest_radius, 0, -crest_shift)

    profile_poly = Part.makePolygon([p1, p2, p3, p4, p1])
    profile_wire = Part.Wire(profile_poly.Edges)

    helix_radius = (root_radius + crest_radius) / 2.0
    helix = Part.makeHelix(max(pitch, 0.1), max(length, 0.2), helix_radius)

    # Sweep thread profile along helix for real geometry thread.
    thread_shape = profile_wire.makePipeShell([helix], True, True)
    if getattr(thread_shape, "ShapeType", "") == "Solid":
        thread = thread_shape
    else:
        thread = Part.Solid(thread_shape)
    core = Part.makeCylinder(root_radius, length)
    return core.fuse(thread)


def build_screw(params):
    diameter = max(params["diameter"], 0.5)
    length = max(params["length"], 1.0)
    head_width = max(params["head_width"], diameter)
    head_length = max(params["head_length"], 0.3)
    pitch = max(params["thread_pitch"], 0.1)
    depth = max(params["thread_depth"], 0.05)
    angle = max(params["thread_angle"], 10.0)
    thread_type = params.get("thread_type", "Custom")
    tol = max(params["tolerance"], 0.0)

    # For standard thread types, use a practical default profile while keeping
    # custom mode fully user-defined.
    if thread_type in ("Metric ISO", "Unified"):
        angle = 60.0
        depth = max(depth, 0.6134 * pitch)

    adjusted_major = max(diameter - 2.0 * tol, diameter * 0.6)

    thread_length = length
    body = _build_thread(adjusted_major, pitch, depth, angle, thread_length)

    head_type = params["head_type"]
    if head_type == "Hex":
        head = _make_hex_head(head_width, head_length)
    elif head_type == "Phillips":
        head = _make_phillips_head(head_width, head_length)
    elif head_type == "Unbraco (Socket Cap)":
        head = _make_socket_cap_head(head_width, head_length)
    elif head_type == "Flat":
        head = _make_flat_head(head_width, head_length)
    else:
        head = _make_pan_head(head_width, head_length)

    head.translate(App.Vector(0, 0, length))
    return body.fuse(head)


class ScrewDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ScrewDialog, self).__init__(parent)
        self.setWindowTitle("Screw Generator")
        self.setMinimumWidth(360)

        layout = QtGui.QFormLayout(self)

        self.preset_combo = QtGui.QComboBox()
        self.preset_combo.addItems(list(PRESETS.keys()))
        self.preset_combo.currentTextChanged.connect(self._apply_preset)

        self.head_type_combo = QtGui.QComboBox()
        self.head_type_combo.addItems(["Hex", "Phillips", "Unbraco (Socket Cap)", "Pan", "Flat"])

        self.thread_type_combo = QtGui.QComboBox()
        self.thread_type_combo.addItems(["Metric ISO", "Unified", "Custom"])

        self.head_width = QtGui.QDoubleSpinBox()
        self.head_width.setRange(0.5, 500.0)
        self.head_width.setSuffix(" mm")

        self.head_length = QtGui.QDoubleSpinBox()
        self.head_length.setRange(0.2, 500.0)
        self.head_length.setSuffix(" mm")

        self.screw_length = QtGui.QDoubleSpinBox()
        self.screw_length.setRange(1.0, 1000.0)
        self.screw_length.setSuffix(" mm")

        self.screw_diameter = QtGui.QDoubleSpinBox()
        self.screw_diameter.setRange(0.5, 200.0)
        self.screw_diameter.setSuffix(" mm")

        self.thread_pitch = QtGui.QDoubleSpinBox()
        self.thread_pitch.setRange(0.1, 50.0)
        self.thread_pitch.setDecimals(3)
        self.thread_pitch.setSuffix(" mm")

        self.thread_depth = QtGui.QDoubleSpinBox()
        self.thread_depth.setRange(0.05, 20.0)
        self.thread_depth.setDecimals(3)
        self.thread_depth.setSuffix(" mm")

        self.thread_angle = QtGui.QDoubleSpinBox()
        self.thread_angle.setRange(10.0, 120.0)
        self.thread_angle.setDecimals(2)
        self.thread_angle.setSuffix(" deg")

        self.thread_tolerance = QtGui.QDoubleSpinBox()
        self.thread_tolerance.setRange(0.0, 2.0)
        self.thread_tolerance.setDecimals(3)
        self.thread_tolerance.setSuffix(" mm")

        layout.addRow("Preset", self.preset_combo)
        layout.addRow("Head Type", self.head_type_combo)
        layout.addRow("Head Width", self.head_width)
        layout.addRow("Head Length", self.head_length)
        layout.addRow("Screw Length", self.screw_length)
        layout.addRow("Screw Diameter", self.screw_diameter)
        layout.addRow("Thread Type", self.thread_type_combo)
        layout.addRow("Thread Pitch", self.thread_pitch)
        layout.addRow("Thread Depth", self.thread_depth)
        layout.addRow("Thread Angle", self.thread_angle)
        layout.addRow("Thread Tolerance", self.thread_tolerance)

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self._apply_preset("Custom")

    def _apply_preset(self, name):
        preset = PRESETS.get(name, PRESETS["Custom"])
        self.screw_diameter.setValue(preset["diameter"])
        self.screw_length.setValue(preset["length"])
        self.head_width.setValue(preset["head_width"])
        self.head_length.setValue(preset["head_length"])
        self.thread_pitch.setValue(preset["thread_pitch"])
        self.thread_depth.setValue(preset["thread_depth"])
        self.thread_angle.setValue(preset["thread_angle"])
        self.thread_tolerance.setValue(preset["tolerance"])
        self.thread_type_combo.setCurrentText(preset["thread_type"])
        self.head_type_combo.setCurrentText(preset["head_type"])

    def get_params(self):
        return {
            "head_type": self.head_type_combo.currentText(),
            "head_width": _safe_float(self.head_width.value(), 5.0),
            "head_length": _safe_float(self.head_length.value(), 2.0),
            "length": _safe_float(self.screw_length.value(), 10.0),
            "diameter": _safe_float(self.screw_diameter.value(), 3.0),
            "thread_type": self.thread_type_combo.currentText(),
            "thread_depth": _safe_float(self.thread_depth.value(), 0.3),
            "thread_angle": _safe_float(self.thread_angle.value(), 60.0),
            "thread_pitch": _safe_float(self.thread_pitch.value(), 0.5),
            "tolerance": _safe_float(self.thread_tolerance.value(), 0.0),
        }


class ScrewGeneratorCommand:
    def GetResources(self):
        return {
            "Pixmap": "",
            "MenuText": "Create Screw",
            "ToolTip": "Open screw generator dialog",
        }

    def Activated(self):
        if App.ActiveDocument is None:
            App.newDocument("ScrewDocument")

        dialog = ScrewDialog(Gui.getMainWindow())
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return

        params = dialog.get_params()
        shape = build_screw(params)

        doc = App.ActiveDocument
        obj = doc.addObject("Part::Feature", "GeneratedScrew")
        obj.Shape = shape
        obj.Label = "Screw_{}x{}".format(
            int(round(params["diameter"] * 10)) / 10.0,
            int(round(params["length"] * 10)) / 10.0,
        )
        doc.recompute()

    def IsActive(self):
        return True
