from zope.interface import Interface


class IJobPerformanceView(Interface):
    def interviews():
        """Return a list of interviews"""

    def improvementAreas():
        """Return improvement areas of last meeting."""
