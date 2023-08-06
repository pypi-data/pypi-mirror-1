import AnalyticsReporting

def initialize(context): 
  "initialize the product"

  context.registerClass(
      AnalyticsReporting.AnalyticsReporting,
      constructors = (
         ('AnalyticsAdd', AnalyticsReporting.manage_addAnalyticsReportingForm), 
         AnalyticsReporting.manage_addAnalyticsReporting
         ),
         icon = 'icon.gif'
  )