"""A folderish object with views for displaying Event contents in calendar form"""

__author__ = 'Lupa Zurven <lupa@zurven.com>'
__docformat__ = 'plaintext'

from Products.CMFCore import permissions
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.Archetypes.BaseFolder import BaseFolder
from Products.CalendarX.config import *

schema = Schema((

	IntegerField(
		name='dayOfWeekToStart',
		widget=SelectionWidget(
			label="Day of Week to Start",
			description="Value indicates what day of the week the Month and Week views begin on.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		vocabulary=[(0, "Sunday"), (1, "Monday"), (2, "Tuesday"), (3, "Wednesday"), (4, "Thursday"), (5, "Friday"), (6, "Saturday",)],
		default=0,
	),

	StringField(
		name='defaultView',
		widget=StringWidget(
			label="Default view template",
			description="Name of the default view to be displayed: month, weekbyday, weekbyhour, or day.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default='month',
	),

	BooleanField(
		name='useAdvancedQuery',
		widget=BooleanWidget(
			label="Use advanced query.",
			description="If checked, CalendarX will use the AdvancedQuery product for making queries to the catalog to find events. Use this if you want to override those query methods in your skin folder. I find AdvancedQuery significantly easier to use in building complex queries, but it offers no other advantages for general use in CalendarX.  AdvancedQuery is included with Plone 3.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=True,
	),

	StringField(
		name='dayViewStartHour',
		widget=StringWidget(
			label="Day view start hour",
			description="Hour of day for CalendarX to BEGIN display for day view and for weekbyhour view. 8 = 8am = 08:00, 20 = 6pm = 20:00. For a 24 hour calendar, set this to 0 (zero).",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=8,
	),

	StringField(
		name='dayViewEndHour',
		widget=StringWidget(
			label="Day view end hour",
			description="Hour of day for CalendarX to END display for day view and for weekbyhour view. 8 = 8am = 08:00, 20 = 6pm = 20:00. For a 24 hour calendar, set this to 0 (zero).",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=20,
	),

	StringField(
		name='earlyDayEventHour',
		widget=StringWidget(
			label="Early day event hour",
			description=""" Hour of day for CalendarX to use for deciding between events being
							classed as "later" or "earlier" in the Day and Weekbyhour views.
							Previous behavior was that events up to midnight showed as "later"
							events and "earlier" events from midnight to dayViewStartHour showed
							up as "continuing".	 This property is the hour that now serves as the
							boundary between these types of events.

						  Default value is 0, representing 12 midnight, meaning there are no "later"
							events.
						  Setting value to 3, will represent 3am.  Seems a reasonable boundary to me,
							meaning that events running 1am-2am will show up on the previous day, say
							Saturday night instead of Sunday morning.

						  Use Case: Calendar of events for a city where there are commonly late
							night movies or concerts after midnight... consider Las Vegas, for example.
							Now you can set the boundary to be 3 or 4am, so that when viewing the Day
							view for Friday, the later events as late as 3am on Saturday morning will
							show up on the Friday view.

						  Limitations: ONLY applies to Day and WeekByHour views, not to other views.
							Therefore this could create some confusion among viewers who see a late
							night event on Saturday night on the Day view, but finding that same event
							displayed on Sunday on the month view.	A fully consistent fix is
							for this situation is difficult, and I'm unwilling to program it at this
							time.  I tried, and hence the long delay between the 0.6.4 and 0.6.5
							releases.  Instead I'm leaving it at this for now.
			""",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=0,
	),

	StringField(
		name='hoursDisplay',
		widget=StringWidget(
			label="Hours Display",
			description="Code to tell the 'hoursdisplay' macro how to display the hours in your calendar views. Currently two possibilities and they only affect the left column display of hours: '12ampm' = 12 hour display, with am or pm. Ex. 6 pm '24.00' = 24 hour display, with period. Ex. 20.00",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default='12ampm',
	),


	BooleanField(
		name='useHalfHours',
		widget=BooleanWidget(
			label="Use half hours.",
			description="If checked, CalendarX will display half-hour increments on the day and weekbyhour views instead of the default one-hour increments.  There remains NO capability of starting the day on the half-hour... the dayViewStartHour and dayViewEndHour settings must be integer hour values. The default value is blank (false), meaning Hourly periods will be used. There is a modest performance penalty associated with this option, use at your discretion.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False,
	),

	StringField(
		name='numMonthsForMultiMonthView',
		widget=StringWidget(
			label="Number of months to display in the multi-month view.",
			description="How many months to display in the month view. Default value is 1, but may be extended up to 12 months.	 Next buttons move forward by one month, not by the number of months in the view.  Querying time to generate several months at once may be excessive if many events are to be shown.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default='3'
	),

	BooleanField(
		name='showHeaderTitleAndIcons',
		widget=BooleanWidget(
			label="Show header title and icons.",
			description="If checked, CalendarX will display the calendar title and description and email/print/favorites Action icons as it does for other Plone content. ",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False,
	),

	BooleanField(
		name='showHighlightFullEvent',
		widget=BooleanWidget(
			label="Show full event highlight",
			description="If checked, CalendarX will show the full extent of Events on the calendar, even without rolling over with the mouse. Default is a blue color, can be changed in CSS property sheet. NOTE! If you use this, you might also want to disable the labelEventsOnlyAtStart property. Disabling labelEventsOnlyAtStart means that the events in the Month view that span several days will show labels for each of those days, instead of only on the first day of the event.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False,
	),

	BooleanField(
		name='showJumpToDateWidget',
		widget=BooleanWidget(
			label="Show jump-to-date widget",
			description="If checked, a date-picking widget will show up at the top and bottom of the calendar near the Next/Previous links. This widget lets users pick a date and jump to it, instead of using multiple Next, Next, Next click, or manually typing the date into the URL querystring.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=True,
	),

	BooleanField(
		name='useNumericMonthInJumpToDateWidget',
		widget=BooleanWidget(
			label="Use numeric month in jump-to-date widget",
			description="If checked, the Jump-To-Date widget will show a numeric month value (ex. '2') instead of an abbreviation of the month (ex. 'Feb'). These abbreviations are pulled from the python DateTime module, not coded into CalendarX code, in the getMonthName.py script.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	BooleanField(
		name='showPublicPrivateLink',
		widget=BooleanWidget(
			label="Show public/private link",
			description="If checked, the *Public* vs *My Events* link will be shown in the Subject Bar.	 This link allows users to switch between viewing all the published events, or ONLY their own private events. If your calendar is mainly for viewing by anonymous users, you probably don't need this.	Default is OFF because this is a nice feature, but not a commonly chosen one. ",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	BooleanField(
		name='useMultiSubjects',
		widget=BooleanWidget(
			label="Use multiple subjects",
			description="If checked, the Subject category picker is a checkbox-style form, allowing users to select multiple subjects for viewing. If unchecked, it switches to (an older) single subject chooser that only allows one Subject category at a time.	Default is ON for this new-style Multi-Subject chooser, because it is ever so much nicer.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=True,
	),

	BooleanField(
		name='showSubjectBar',
		widget=BooleanWidget(
			label="Show subject bar",
			description="If checked, the Subject bar is shown, and if unchecked, it will disappear from view.  Default is ON.  Decomplicates the calendar if you don't want to use Public/Private or Subject categories.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=True
	),

	BooleanField(
		name='useCalendarHelp',
		widget=BooleanWidget(
			label="Use calendar help",
			description="Check this attribute to show a View tab for 'Calendar Help'.  This brings up a new view page that is intended for you to use for help in case you have neophyte users who could use some calendar help.  I've added some code that brings up one page of help for 'Members' and a different page of help for 'Anonymous' users.  This could easily be extended to show different help screens for other Roles.	 See the 'help' view page template for more information.  The help text is quite minimal, so feel free to expand it for your users.	 Feel free to send me a copy of your nice help files, too!",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	BooleanField(
		name='includeReviewStateVisible',
		widget=BooleanWidget(
			label="Include 'visible' events",
			description="Check this attribute to include events where the review state is 'visible' as well as 'published'.  This is useful for calendars where the only users are trusted users and going through the publishing workflow only adds unnecessary complication.  In particular, this could work well even on a site with many untrusted users.  In that case, create a calendar for the trusted users that uses a repurposed Event with a new portal_type name. Use the 'restrictToThisListOfTypes' attribute to make this new calendar ONLY read this one type of Event.  Then use a getNotAddableTypes.py script to restrict the use of this type of Event to your trusted users (as a role, or a group, or whatever). See the HowTo on plone.org for use of getNotAddableTypes.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=True
	),

	BooleanField(
		name='showPendingLink',
		widget=BooleanWidget(
			label="Show pending link",
			description=" Check this attribute to show a link in the subjectbar that, when clicked, tells the calendar to display events with 'pending' state as well as the  other events (published, and visible if includeReviewStateVisible has been  selected).  The link is not a toggle; to get out of the mode where the  pending events are showing, simply click any other link on the calendar.This link ONLY shows up for Calendar Managers.  Who is a Calendar Manager? User status as a Calendar Manager is determined by the isCalendarManager.py  script.  It is easily customized, but as a default is set to allow users with the 'Manager' role.	 If this role is adequate for you, leave this script as is.  An example is included in the script to show how to look up group membership to determine Calendar Manager status. ",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	BooleanField(
		name='showPrivateEventsToGroupMembers',
		widget=BooleanWidget(
			label="Show private events to group members",
			description=" Check this attribute to allow PRIVATE events to show up to anyone with the Plone privilege of viewing your PRIVATE events.  In short, what this does is allow you to give one of your Groups or some other user a proxy  ownership role for one of your review_status=Private events.	 That is enough to allow them to see it in Plone.	But this attribute must be TRUE (checked) if you want such events to show up on a CalendarX  instance.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	LinesField(
		name='listOfReviewStatesDisplayed',
		widget=LinesWidget(
			label="List of review states to be displayed",
			description="List each review state, one per line (e.g., 'published', 'external', 'internal', 'internally_published', 'pending', 'private', 'visible', etc.) that you wish to be displayed in your CalendarX.  These states will be appended to the list of any other review state choices you've made using other attributes.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default= ('published','external','internal','internally_published'),
	),

	BooleanField(
		name='showOnlyEventsInMonth',
		widget=BooleanWidget(
			label="Show only events in current month",
			description="Check this attribute to restrict the Month view to display events ONLY in the current calendar month, and NOT those events that occur in the days before or after the month begins and ends (ie., if the month view shows the 30th and 31st of the previous month on the calendar, events will NOT be displayed for those dates.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	BooleanField(
		name='labelEventsOnlyAtStart',
		widget=BooleanWidget(
			label="Only label multi-day events on the first day.",
			description="Check this attribute to put labels on the month view ONLY on the first day of an event that lasts multiple days.  Default is SELECTED.	 Unselect thisattribute if you'd like the event title and datestring to appear on each calendar day that the event is on (ie., a four day event will have the labelshow up on the calendar four times, on each of the four days of the event). NOTE!  Disabling this (to show events on EVERY day) will only work if the showHighlightFullEvent property is turned ON (selected).  It would make no sense (to me) to have the event labeled, but not highlighted.  So make sureyou use these together.	No harm if you don't, but it won't behave the way you might have expected.	It pays to read the documentation.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=True,
	),

	LinesField(
		name='listOfSubjects',
		widget=LinesWidget(
			label="List of subjects",
			description="List of the subjects in your CalendarX, for use in	creating the macro that displays them on your calendar.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
	),

	BooleanField(
		name='restrictToThisListOfSubjects',
		widget=BooleanWidget(
			label="Restrict to this list of subjects",
			description="Display only those subjects listed above",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	LinesField(
		name='eventTypes',
		widget=LinesWidget(
			label="List of event types",
			description="A list of the portal_types to display in the calendar.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
	),

	BooleanField(
		name='restrictToThisListOfTypes',
		widget=BooleanWidget(
			label="Restrict to this list of types",
			description="Display only those types listed above",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	LinesField(
		name='listOfPaths',
		widget=LinesWidget(
			label="List of paths",
			description="A list of the paths to look for events.",
			i18n_domain="CalendarX",
		),
		schemata="Calendar Options",
	),

	BooleanField(
		name='restrictToThisListOfPaths',
		widget=BooleanWidget(
			label="Restrict to only these paths",
			description="Display only events found in the paths above.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	BooleanField(
		name='restrictToThisFolder',
		widget=BooleanWidget(
			label="Restrict to this folder",
			description="Display only events found within or beneath the parent folder of this CalendarX instance.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	LinesField(
		name='listOfSubjectTitles',
		widget=LinesWidget(
			label="List of subject titles",
			description="Provide a list of shorter titles for each of your subjects.",
			i18n_domain="CalendarX",
		),
		schemata="Calendar Options",
	),

	BooleanField(
		name='useSubjectTitles',
		widget=BooleanWidget(
			label="Use subject titles",
			description="Display the subject title defined above.",
			i18n_domain="CalendarX"
		),
		schemata="Calendar Options",
		default=False
	),

	## Event Display Properties (CX_props_eventdisplays_text) ##

	BooleanField(
		name='useSubjectIcons',
		widget=BooleanWidget(
			label="Use Subject Icons",
			description="If checked, this will cause the views to choose an icon for each event based on the Subject names found in the list.",
			i18n_domain="CalendarX"
		),
		schemata='Event Display Properties',
		default=False
	),

	LinesField(
		name='listOfSubjectIcons',
		widget=LinesWidget(
			label="Subject Icons",
			description="The list consists of a lines attribute where each line consists of a Subject and an icon ID, separated by a pipe ( | ) character.	For example: Work|event_work_icon.gif where Work is the subject. Your subject names should (must!) match the actual subjects you use for your events, or this method will not work well.  Actually, it will just pull the default event_icon.gif from the Plone skin if there is any problem finding a matching subject name or icon ID. This property is handy for making your events more visibly recognizable in your calendar page. The default icon size is 16x16 pixels, with some white (or clear) pixel space on the right and left sides.	I haven't tested it with larger icons, but keeping to a modest size might be a good idea. Add your event icons into your /portal_skins/custom folder, or put them directly into your calendar instance folder for (slightly) better performance.",
			i18n_domain="CalendarX"
		),
		schemata='Event Display Properties',
	),

	BooleanField(
		name='useSubjectCSSClasses',
		widget=BooleanWidget(
			label="Use Subject CSS Classes",
			description="If checked, this will cause the views to choose a CSS class for each event based on the Subject names found in the list.",
			i18n_domain="CalendarX"
		),
		schemata='Event Display Properties',
		default=False
	),

	LinesField(
		name='listOfSubjectCSSClasses',
		widget=LinesWidget(
			label="Subject CSS Classes",
			description="The list consists of a lines attribute where each line consists of a Subject and a CSS class name, separated by a pipe ( | ) character.  For example: US Holiday|event_usholiday where Work is the subject, and event_usholiday is the CSS class name. Your subject names should (must!) match the actual subjects you use for your events, or this method will not work well.	 Actually, it will just pull the default event_published CSS class from the Plone skin if there is any problem finding a matching subject name or icon ID. This nicely allows you to apply styles like font color to your event listings according to the Subject of the event.	 Put your custom styles into your calendar.css stylesheet, or into a customized version of the ploneCustom.css stylesheet if you prefer (the sample ones I've created for default use are found in calendar.css). Additionally, if you want the Subjects in the Subject listing at the top of the calendar to reflect these same CSS classes, you have to add these too. Example ones (for Appointment, etc.) are in calendar.css for you to customize. *** ONE MORE NOTE about these.	Make sure in your listOfSubjectCSSClasses and listOfSubjectIcons lines properties that you use the actual SUBJECT name and not any Subject nicknames you might use for display (as defined in the listOfSubjectTitles property in CX_props_calendar. Those labels won't work here, only the actual subject will work. *** AND ONE MORE NOTE.  The following two properties (useEventTypeIcons and useEventTypeCSSClasses) take precedence over useSubjectTypeIcons and useSubjectCSSClasses if, for unknown reasons, BOTH have been selected. There's no real reason to select both... only one can work at a time, and I chose to make the EventType ones take priority.  Go figure.",
			i18n_domain="CalendarX"
		),
		schemata='Event Display Properties',
	),

	BooleanField(
		name='useEventTypeIcons',
		widget=BooleanWidget(
			label="Use Event Type Icons",
			description="If checked, this will cause the views to choose an icon for each event based on the Event Type (portal_type).",
			i18n_domain="CalendarX"
		),
		schemata='Event Display Properties',
		default=False
	),

	LinesField(
		name='listOfEventTypeIcons',
		widget=LinesWidget(
			label="Event Type Icons",
			description="The list consists of a lines attribute where each line consists of an Event Type and an icon ID, separated by a pipe ( | ) character.	For example: Event|event_icon.gif where Event is the portal_type.",
			i18n_domain="CalendarX"
		),
		schemata='Event Display Properties',
	),

	BooleanField(
		name='useEventTypeCSSClasses',
		widget=BooleanWidget(
			label="Use Event Type CSS Classes",
			description="If checked, this will cause the views to choose a CSS class for each event based on the Event Type (portal_type).",
			i18n_domain="CalendarX"
		),
		schemata='Event Display Properties',
		default=False
	),

	LinesField(
		name='listOfEventTypeCSSClasses',
		widget=LinesWidget(
			label="Event Type CSS Classes",
			description="The list consists of a lines attribute where each line consists of a Subject and a CSS class name, separated by a pipe ( | ) character.  For example: AT Event|atevent_class where AT Event is the portal_type, and atevent_class is the CSS class name.",
			i18n_domain="CalendarX"
		),
		schemata='Event Display Properties',
	),

	## End of Event Display Properties ##

	## Sub Topic Calendar Properties (CX_props_subcalendar_text) ##

	BooleanField(
		name='useSubCalendarSubjectMenu',
		widget=BooleanWidget(
			label="Sub Calendar Menu",
			description="For MAIN Calendars: Check this property to signal that (1) there are subcalendars below and (2) hence, use the special SubCalendar Menu for the Subject Links that allows you to both (either) filter on the subcalendars as well as click on the Subject (subcalendar name) to drill down and view that subcalendar alone.",
			i18n_domain="CalendarX"
		),
		schemata="Sub Calendar Properties",
		default=False
	),

	LinesField(
		name='listOfSubCalendarIDs',
		widget=LinesWidget(
			label="List of SubCalendar IDs",
			description="For MAIN Calendars: This is a list (one per line) of the IDs of the subcalendars.  The menu choices uses this list for the URL links to subcalendars.",
			i18n_domain="CalendarX"
		),
		schemata="Sub Calendar Properties",
		default="",
	),

	LinesField(
		name='listOfSubCalendars',
		widget=LinesWidget(
			label="List of SubCalendar Names",
			description="For MAIN Calendars: This is a list (one per line) of names (or nicknames) of the subcalendars.  The menu choices uses this list for display of links to the subcalendars. USE THE SAME ORDER AS IN THE List of SubCalendar IDs ABOVE.",
			i18n_domain="CalendarX"
		),
		schemata="Sub Calendar Properties",
		default="",
	),

	BooleanField(
		name='isSubCalendar',
		widget=BooleanWidget(
			label="Sub Calendar",
			description="For SUB Calendars:   Check this property if this CalendarX folder is a subcalendar.  This controls the style of menu displayed for subcalendars versus non-subcalendars.",
			i18n_domain="CalendarX"
		),
		schemata="Sub Calendar Properties",
		default=False
	),

	StringField(
		name='nameOfSubCalendar',
		widget=StringWidget(
			label="Name of Sub Calendar",
			description="For SUB Calendars:   The name of this subcalendar.  This is displayed in the Subject Links area on the subcalendar (and is NOT used on the Main calendar).",
			i18n_domain="CalendarX"
		),
		schemata="Sub Calendar Properties",
	),

	## End of Sub Calendar Properties (CX_props_subcalendar_text) ##

	BooleanField(
		name='showPOPTitle',
		widget=BooleanWidget(
			label="Show Pop Title",
			description="Whether to show the Title of the event",
		   	i18n_domain="CalendarX"
		),
		schemata="Pop up Properties",
		default=False
	),
	BooleanField(
		name='showPOPType',
		widget=BooleanWidget(
			label="Show Pop Type",
			description="Whether to show the Type string, telling what type of event object is showing up in the calendar",
		   	i18n_domain="CalendarX"
		),
		schemata="Pop up Properties",
		default=False
	),
	BooleanField(
		name='showPOPSubject',
		default=True,
		widget=BooleanWidget(
			label="Show Pop Subject",
			description="Whether to show the Subject of the event",
			i18n_domain="CalendarX"
		),
		schemata="Pop up Properties",
	),

	BooleanField(
		name='showPOPStart',
		widget=BooleanWidget(
			label="Show Pop Start",
			description="Whether to show the Start date and time of the event",
			i18n_domain="CalendarX"
		),
		schemata="Pop up Properties",
		default=False
	),
	BooleanField(
		name='showPOPEnd',
		widget=BooleanWidget(
			label="Show Pop End",
			description="Whether to show the End date and time of event",
			i18n_domain="CalendarX"
		),
		schemata="Pop up Properties",
		default=False
	),
	BooleanField(
		name='showPOPCreator',
		widget=BooleanWidget(
			label="Show Pop Creator",
			description="Whether to show the Creator (Plone username) for this event",
			i18n_domain="CalendarX"
		),
		schemata="Pop up Properties",
		default=False
	),
	BooleanField(
		name='showPOPCreated',
		widget=BooleanWidget(
			label="Show Pop Created",
			description="Whether to show the Created date of the event",
			i18n_domain="CalendarX"
		),
		schemata="Pop up Properties",
		default=False
	),
	BooleanField(
		name='showPOPModified',
		widget=BooleanWidget(
			label="Show Pop Modified",
			description="Whether to show the Modified date of the event, when the last time this event was edited",
			i18n_domain="CalendarX"
		),
		schemata="Pop up Properties",
		default=False
	),
	BooleanField(
		name='showPOPState',
		widget=BooleanWidget(
			label="Show Pop State",
			description="Whether to show the review State of the event, such as published, visible, etc.",
            i18n_domain="CalendarX"
		),
		schemata="Pop up Properties",
		default=False
	),
	BooleanField(
		name='showPOPDescription',
		default=True,
		widget=BooleanWidget(
			label="Show Pop Description",
			description="Whether to show the Description of the event",
			i18n_domain="CalendarX"
		),
		schemata="Pop up Properties",
	),

	## Add Event Link Properties (CX_props_addeventlink) ##

	BooleanField(
		name='showAddEventLink',
		widget=BooleanWidget(
			label="Show Add Event Link?",
			description="Check this to include an Add New Event link in the SubjectLinks bar. Controls for this link are below.	 If more than one of the boolean controls below are checked, the ones below will take priority over the ones above.	 For example, if both useANEFolder and useRolesAndFolders are checked, but the current user does not have one of the specified Roles, then the link target will fall back to the specified ANEFolderPath.  The order of these priorities is determined by the code in the Python script getAddNewEventURL.	If no match is found, then a blank string will be returned to the macro, and a condition there will cause NO Add New Event link to be shown.  This way you can restrict display of this link to only certain users or to users with certain roles.	The first two choices (useMemberFolder and useANEFolder) are shown to all Authenticated users, if selected.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default=False
	),

	BooleanField(
		name='useCreateObjectOnClick',
		widget=BooleanWidget(
			label="Use Create Object On Click",
			description="Together, these two properties tell the link to instantiate a new Event object in the target folder.  Check this if you want to have the link automatically initiate editing of a new event for the user.	Uncheck this property if you want the Add New Event link to simply take the user to a target folder without starting a new Event object automatically.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default=True
	),

	StringField(
		name='createObjectOnClickCommand',
		widget=StringWidget(
			label="Create Object On Click Command",
			description="The createObjectOnClickCommand string is the command that is carried in the query string of the link's URL target if you are using the useCreateObjectOnClick property.  The default string is: createObject?type_name=Event which will create a new Event object in the target folder of the link. If you have a different event type that you would like to create, replace the meta_name Event with the appropriate meta_name of your desired event type. If you use this feature, it is advisable to also set your portal to use the portal_factory for initiating Events, so that if a user clicks on the link to start a new event but then decides not to finish it, the event will not be abandoned half-finished.	 Portal_factory will simply create a temporary version and then delete it if left unfinished by the user.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
	),

	BooleanField(
		name='useMemberFolder',
		widget=BooleanWidget(
			label="Use Member Folder",
			description="Check this so that the link will take users to their default Member folder where they can add Events. *WARNING* If your users do not have a default Member folder, or if it is located somewhere funny (not in mysite/Members/username) then this option may cause an error for your users.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default=True
	),

	BooleanField(
		name='useMemberSubfolder',
		widget=BooleanWidget(
			label="Use Member Subfolder",
			description="NOTE: ONLY WORKS IF THERE EXISTS A MEMBER'S HOME FOLDER: THERE IS NONE BY DEFAULT IN PLONE 3.0+.  Check this property if you want events to be instantiated in a subfolder of a user's Member folder.  For example, if all your users are musicians in bands (or groupies perhaps) and they post their band gigs on the calendar, then you might want all the events to be saved in a specific subfolder, such as /Members/username/gigs.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default=False
	),

	StringField(
		name='memberSubfolderPath',
		widget=StringWidget(
			label="Member Subfolder Path",
			description="NOTE: ONLY WORKS IF THERE EXISTS A MEMBER'S HOME FOLDER: THERE IS NONE BY DEFAULT IN PLONE 3.0+.  The proper format for the target folder is relative to the /Members/username folder and should start with a slash, e.g.: /gigs NOTE:  ONLY use this if you are certain that users WILL have the named subfolder in their user folder.	Otherwise it will return 404, page not found error, or default to a folder of this name in the portal root, which is not perhaps what you were wanting.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default="/subfoldername"
	),

	BooleanField(
		name='useANEFolder',
		widget=BooleanWidget(
			label="Use a Named Folder",
			description="Together, these allow you to specify a single folder that will be the target of the link.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default=False
	),

	StringField(
		name='ANEFolderPath',
		widget=StringWidget(
			label="Named Folder Path",
			description="The proper format for the target folder is relative to the portal_root and should start with a slash, e.g.: /somefolderintheroot/thefolderforevents",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default="/thecalendar/thefolderofevents"
	),

	BooleanField(
		name='useUsersAndFolders',
		widget=BooleanWidget(
			label="Use Users and Folders",
			description="Together, these allow you to specify a combination of a username and a corresponding single folder that will be the target of the link for that specific user.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default=False,
	),

	LinesField(
		name='listOfUsersAndFolders',
		widget=LinesWidget(
			label="List of Users and Folders",
			description="The proper format for each line is as follows: username|folderpath where the pipe character (a vertical slash) is used as a separator between the username and folder path.  The proper format for the target folder is relative to the portal_root and should start with a slash, e.g.: /somefolderintheroot/thefolderforevents. An example with two possible role|folder lines: lupa|/calendar/specialevents davos|/calendar/drearyevents If no matching username is found, the priority rules described above will take over to find a suitable target for the user.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default="",
	),

	BooleanField(
		name='useRolesAndFolders',
		widget=BooleanWidget(
			label="Use Roles and Folders",
			description="Together, these allow you to specify a combination of a Role and a corresponding single folder that will be the target of the link for all users with that Role.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default=False,
	),

	LinesField(
		name='listOfRolesAndFolders',
		widget=LinesWidget(
			label="List of Roles and Folders",
			description="The proper format for each line is as follows: rolename|folderpath. where the pipe character (a vertical slash) is used as a separator between the role name and folder path.	The proper format for the target folder is relative to the portal_root and should start with a slash, e.g.: /somefolderintheroot/thefolderforevents. An example with two possible role|folder lines: Manager|/calendar/specialevents Member|/calendar/ordinaryevents The lookup stops when a matching role is found for the user.  For example, if the Manager logs in, the link for the Manager will target the folder called specialevents, even though the Manager is also (likely) a Member of the site.  If no matching role is found, the priority rules described above will take over to find a suitable target for the user.",
			i18n_domain="CalendarX"
		),
		schemata='Add Event Link Properties',
		default="",
	),

	## Add CSS Properties (CX_props_css) ##

	StringField(
		name='viewTabsBorderColor',
		widget=StringWidget(
			label="View tabs border color",
			description='VIEW: These attributes control aspects of the "view" tabs, (month, week, day, etc. view template names) right at the top where you choose which view of the calendar is showing.  View tabs border color.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#8cacbb"
	),

	StringField(
		name='viewTabsBackgroundColor',
		widget=StringWidget(
			label="View tabs background color",
			description="View tabs background color",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#dee7ec"
	),

	StringField(
		name='viewFontBaseSize',
		widget=StringWidget(
			label="View tabs font size",
			description="View tabs font size",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="95%"
	),

	StringField(
		name='viewFontFamily',
		widget=StringWidget(
			label="View tabs font family",
			description="View tabs font family",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='"Lucida Grande", Verdana, Lucida, Helvetica, Arial, sans-serif'
	),

	StringField(
		name='viewTabsFontColor',
		widget=StringWidget(
			label="View tabs font color",
			description="View tabs font color",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#436976"
	),

	StringField(
		name='subjectBarBorderColor',
		widget=StringWidget(
			label="Color of the border around the subject bar",
			description='Subject Bar: These attributes control aspects of the subject bar, where the Private/Public and MetaCalendar Subject choices are found.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#436976"
	),

	StringField(
		name='subjectBarBackgroundColor',
		widget=StringWidget(
			label="Color of the background for subject bar and My:Public bar",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#dee7ec"
	),

	StringField(
		name='subjectFontFamily',
		widget=StringWidget(
			label="Font family for the subject bar and My:Public bar",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='"Lucida Grande", Verdana, Lucida, Helvetica, Arial, sans-serif'
	),

	StringField(
		name='subjectFontSize',
		widget=StringWidget(
			label="Font size for the subject bar and My:Public bar",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="97%"
	),

	StringField(
		name='subjectBarFontColor',
		widget=StringWidget(
			label="Font Color for the subject bar and My:Public bar",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#436976"
	),

	StringField(
		name='headerCenterFontSize',
		widget=StringWidget(
			label='Header font size (e.g. "July 2009")',
			description='Header: These attributes control aspects of the header area, where the previous and next date arrows, and the calendar date are displayed, at the bottom and top of the calendar.  Code for this is generated in the "prevnextcurrentlinks" macro.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="135%"
	),

	StringField(
		name='headerSideFontSize',
		widget=StringWidget(
			label='"previous" and "next" links font size',
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="93%"
	),

	StringField(
		name='headerFontFamily',
		widget=StringWidget(
			label='Font Family name for "prevnextcurrentlinks" macro',
			description="(prev, next, date header, footer)",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='Verdana, Helvetica, Arial, sans-serif'
	),

	StringField(
		name='headerFontColor',
		widget=StringWidget(
			label="Color of the font for header",
			description="(prev, next, date header, footer)",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#436976"
	),

	StringField(
		name='headerHeight',
		widget=StringWidget(
			label='Height added to base for "prevnextcurrentlinks" macro',
			description="(prev, next, date header, footer)",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="0px"
	),

	StringField(
		name='headerMarginBottom',
		widget=StringWidget(
			label='Bottom margin pixels for "prevnextcurrentlinks" macro',
			description="(prev, next, date header, footer)",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="0px"
	),

	StringField(
		name='headerMarginTop',
		widget=StringWidget(
			label='Top margin pixels for "prevnextcurrentlinks" macro',
			description="(prev, next, date header, footer)",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="0px"
	),

	StringField(
		name='headerPadding',
		widget=StringWidget(
			label='Padding size for "prevnextcurrentlinks" macro',
			description="(prev, next, date header, footer)",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="3px"
	),

	StringField(
		name='continuingHeaderFontSize',
		widget=StringWidget(
			label="Continuing events box, header font size",
			description='Continuing: These attributes control aspects of the Continuing Events section, where events that start before or extend across the entire period of view are shown.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="90%"
	),

	StringField(
		name='continuingHeaderFontFamily',
		widget=StringWidget(
			label="Continuing events box, header font family",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="Verdana, Helvetica, Arial, sans-serif"
	),

	StringField(
		name='continuingOuterBorderColor',
		widget=StringWidget(
			label="Continuing events box, outer border color",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#B3CFD9"
	),

	StringField(
		name='continuingOuterBorderWidth',
		widget=StringWidget(
			label="Continuing events box, outer border width",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="1px"
	),

	StringField(
		name='continuingHeaderBorderColor',
		widget=StringWidget(
			label="Continuing events box, inner border color",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#436976"
	),

	StringField(
		name='continuingHeaderBorderWidth',
		widget=StringWidget(
			label="Continuing events box, border width",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="1px"
	),

	StringField(
		name='continuingHeaderBackgroundColor',
		widget=StringWidget(
			label="Continuing events box, background color",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#8CACBB"
	),

	StringField(
		name='continuingRowEventBackgroundColor',
		widget=StringWidget(
			label="Continuing events box, color if an event is present",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#DEE7EC"
	),

	StringField(
		name='continuingRowNoEventBackgroundColor',
		widget=StringWidget(
			label="Continuing events box, color if no event",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#F7F9FA"
	),

	StringField(
		name='continuingRowHeight',
		widget=StringWidget(
			label="Continuing events box, row height, added to event bottom",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="5px"
	),

	StringField(
		name='calBorderColor',
		widget=StringWidget(
			label="Main calendar, border color",
			description='Cal: These attributes control aspects of the Main Calendar display.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#B3CFD9"
	),

	StringField(
		name='calBorderWidth',
		widget=StringWidget(
			label="Main calendar, border width",
			description="",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="1px"
	),

	StringField(
		name='calTableRowOddBackgroundColor',
		widget=StringWidget(
			label="Odd row background color for TR tags",
			description="Main calendar, for certain views where odd/even vary in color, this controls the ODD row (in TR tags).",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#F7F9FA"
	),

	StringField(
		name='calTableRowEvenBackgroundColor',
		widget=StringWidget(
			label="Even row background color for TR tags",
			description="Main calendar, for certain views where odd/even vary in color, this controls the EVEN row (in TR tags)",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#DEE7EC"
	),

	StringField(
		name='calTableHeaderBackgroundColor',
		widget=StringWidget(
			label="Background color for TH tags",
			description="Main calendar, TH tags background color.",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#8CACBB"
	),

	StringField(
		name='calTableHeaderBorderColor',
		widget=StringWidget(
			label="Border color for TH tags",
			description="Main calendar,  TH tags border color.",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#436976"
	),

	StringField(
		name='calTableHeaderBorderWidth',
		widget=StringWidget(
			label="Border width for TH tags",
			description="Main calendar,  TH tags border width.",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="1px"
	),

	StringField(
		name='calTableHeaderFontColor',
		widget=StringWidget(
			label="Font color for TH tags",
			description="Main calendar,  TH tags font color.",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#FFFFFF"
	),

	StringField(
		name='calEventFontSize',
		widget=StringWidget(
			label="Event font size",
			description="Main calendar, font size for the event listings.",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="85%"
	),

	StringField(
		name='calEventFontFamily',
		widget=StringWidget(
			label="Event font family",
			description="Main calendar, font family for the event listings.",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="Verdana, Helvetica, Arial, sans-serif"
	),

	StringField(
		name='calEventPendingTextColor',
		widget=StringWidget(
			label="Pending event text color",
			description='Main calendar, text color for the pending event listings.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#436976'
	),

	StringField(
		name='calEventPrivateTextColor',
		widget=StringWidget(
			label="Private event text color",
			description='Main calendar, text color for the private event listings.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#821513'
	),

	StringField(
		name='calEventPublishedTextColor',
		widget=StringWidget(
			label="Published event text color",
			description='Main calendar, text color for the published event listings.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#466A06'
	),

	StringField(
		name='calEventVisibleTextColor',
		widget=StringWidget(
			label="Visible event text color",
			description='Main calendar, text color for the visible event listings.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#436976'
	),

	StringField(
		name='calTableDataFontColor',
		widget=StringWidget(
			label="Font color for daily calendar cell",
			description='Main calendar, TD tag text color, but is overridden by other CSS rules, mainly.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#000000'
	),

	StringField(
		name='calTableDataBorderColor',
		widget=StringWidget(
			label="Border color for daily calendar cell",
			description='Main calendar, TD tag border color.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#DEE7EC'
	),

	StringField(
		name='calTableDataBorderWidth',
		widget=StringWidget(
			label="Border width for daily calendar cell",
			description='Main calendar, TD tag border width.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='1px'
	),

	StringField(
		name='calTableDataNoEventBackgroundColor',
		widget=StringWidget(
			label="Background color for daily calendar cell with no event",
			description='Main calendar, color when a cell has NO EVENT.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#F7F9FA'
	),

	StringField(
		name='calTableDataEventBackgroundColor',
		widget=StringWidget(
			label="Background color for daily calendar cell with Events",
			description="Main calendar, color when a cell has an EVENT.  Also used in calendar.js.dtml for rollover highlighting return value.",
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default="#DEE7EC"
	),

	StringField(
		name='calTableDataOutOfMonthBackgroundColor',
		widget=StringWidget(
			label="Background color for out-of-month calendar cell",
			description='Main calendar, in the MONTH view when the day shown is NOT a part of the month, this controls the background color.  Also used in calendar.js.dtml for rollover highlighting return value.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#FFFFFF'
	),

	StringField(
		name='calTableDataOutOfMonthBorderColor',
		widget=StringWidget(
			label="Border color for out-of-month calendar cell",
			description='Main calendar, in the MONTH view when the day shown is NOT a part of the month, this controls the border color.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#F7F9FA'
	),

	StringField(
		name='calTableDataOutOfMonthBorderWidth',
		widget=StringWidget(
			label="Border width for out-of-month calendar cell",
			description='Main calendar, in the MONTH view when the day shown is NOT a part of the month, this controls the border width.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='1px'
	),

	StringField(
		name='calTableDataSpanDayFontColor',
		widget=StringWidget(
			label="Font color for date in month view daily calendar cell",
			description='Main calendar, in the MONTH view, text color of the date (ie., "3" on June 3 cell).',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#000000'
	),

	StringField(
		name='calTableDataHeightMonthView',
		widget=StringWidget(
			label="Empty height of daily calendar cell in Month view",
			description='Main calendar, in the MONTH view, this controls the empty height of a daily cell.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='105px'
	),

	StringField(
		name='calTableDataHeightDayView',
		widget=StringWidget(
			label="Empty height of daily calendar cell in Day view",
			description='Main calendar, in the DAY view, this controls the empty height of a daily cell.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='35px'
	),

	StringField(
		name='calTableDataHeightWeekbydayView',
		widget=StringWidget(
			label="Empty height of daily calendar cell in WeekByDay view",
			description='Main calendar, in the WEEKBYDAY view, this controls the empty height of a daily cell.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='105px'
	),

	StringField(
		name='calTableDataHeightWeekbyhourView',
		widget=StringWidget(
			label="Empty height of daily hour cell in WeekByHour view",
			description='Main calendar, in the WEEKBYHOUR view, this controls the empty height of a daily cell.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='30px'
	),

	StringField(
		name='calTableDataFontSizeHour',
		widget=StringWidget(
			label="Font size for hour in daily calendar cell",
			description='Main calendar, in the DAY and WEEKBYHOUR views, this controls the font size of the HOUR displayed (ie., "8am" or "13:00")',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='130%'
	),

	StringField(
		name='calTableDataEventHighlightBackgroundColor',
		widget=StringWidget(
			label="Background color for event rollover in daily calendar cell",
			description='Main calendar, in the view when an event has a mouseover (rollover) event, this controls the rollover background color.  Read into calendar.js.dtml for this control.',
			i18n_domain="CalendarX"
		),
		schemata='CSS Properties',
		default='#FFE7C4'
	),

	## End of Schema Properties  ##

),
)

CalendarXFolder_schema = BaseFolder.schema.copy() + schema.copy()

class CalendarXFolder(BaseFolder):
    """CalendarX is a folder (so it can hold other CalendarX subcalendars)
    Based on Archetypes, it has many configurable properties.
    """
    security = ClassSecurityInfo()
    __implements__ = (BaseFolder.__implements__, (),)

	# This name appears in the 'add' box
    archetype_name = 'CalendarX'

    meta_type = 'CalendarXFolder'
    portal_type = 'CalendarXFolder'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 1
    content_icon = 'CalendarX16.gif'
    immediate_view = 'showDefaultView'
    default_view = 'showDefaultView'
    suppl_views = ()
    typeDescription = "CalendarXFolder"
    typeDescMsgId = 'description_edit_calendarxfolder'

    # Make sure we get title-to-id generation when an object is created
    _at_rename_after_creation = True

    schema = CalendarXFolder_schema

    aliases = {
        '(Default)'  : 'showDefaultView',
        'index.html' : '(Default)',
        'edit'       : 'base_edit',
        'properties' : 'base_metadata',
        'sharing'    : '',
        'view'       : '(Default)',
        }

registerType(CalendarXFolder, PROJECTNAME)
