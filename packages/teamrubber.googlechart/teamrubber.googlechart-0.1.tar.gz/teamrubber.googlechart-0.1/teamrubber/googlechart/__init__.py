from teamrubber.googlechart.chart import ZGoogleChart, addChart, manage_addChart

def initialize(registrar):
    registrar.registerClass(
        ZGoogleChart,
        permission = 'Add Documents, Images, and Files',
        icon = 'dtml/googlechart.png',
        constructors = (manage_addChart, addChart),
        )
