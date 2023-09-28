# FRC 190 Website

---

## Version 1.0.0
* Database: SQLite
* User functionality:
  * Account: 
    * view name, email, and type of user
    * update profile picture
    * reset password
    * view recently logged hours
    * view hours summary
  * Events:
    * view events sorted by upcoming and previous
    * view event details, and who else is signed up
    * sign up for events in advance to show interest
    * log hours for events after they begin
* Admin functionality (in addition to regular user functionality):
  * Account:
    * register new users
  * Events:
    * create, edit, and delete events
  * Hours:
    * approve users' logged hours

## Ideas for Next Version
* Database: PostgreSQL?
* Improve hours summary visuals
* Do account setup and password resets through email
* Allow users to log in with WPI?
* Notifications through email
* Import and/or export events from Outlook/Google/iCloud calendars or iCal files
* Integration with Slack
* When creating events, make option for recurring (ex. every Wednesday until 12/15/2023)
* Allow users to comment on events (with questions, meeting summaries, etc.)
* Integration with scouting app
