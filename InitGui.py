import FreeCADGui


class ScrewGeneratorWorkbench(FreeCADGui.Workbench):
    MenuText = "SnartScrews"
    ToolTip = "SnartScrews: create screws with parameterized head and thread settings."
    Icon = """
/* XPM */
static char * screw_generator_xpm[] = {
"16 16 3 1",
"  c None",
". c #2B2B2B",
"+ c #D0D0D0",
"                ",
"      ....      ",
"     .++++.     ",
"    .++++++.    ",
"    .++++++.    ",
"      .++.      ",
"      .++.      ",
"      .++.      ",
"      .++.      ",
"      .++.      ",
"      .++.      ",
"      .++.      ",
"      .++.      ",
"      ....      ",
"                ",
"                "};
"""

    def Initialize(self):
        # Import here so a module-level import error does not hide the workbench.
        from screw_generator import ScrewGeneratorCommand

        FreeCADGui.addCommand("ScrewGenerator_Create", ScrewGeneratorCommand())
        self.appendToolbar("SnartScrews", ["ScrewGenerator_Create"])
        self.appendMenu("SnartScrews", ["ScrewGenerator_Create"])

    def Activated(self):
        pass

    def Deactivated(self):
        pass


FreeCADGui.addWorkbench(ScrewGeneratorWorkbench())
