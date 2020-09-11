ReadyRaider's Guild Management Discord Bot!
===========================================

How to Use the Bot:
-------------------

Our discord bot links to our comprehensive World of Warcraft Classic guild management web application. In order to start you must create your guild by visiting [ReadyRaider](https://www.readyraider.com/dashboard) . After you have created your account and guild, link your discord profile on your account page. When the bot is invited to the server be sure to use the $set command (Must have discord account linked) to attach the bot to your guild.

All functions between the web application and the discord bot change in real time. You can use the web application to create and confirm events, populate loot tables, handle complex guild functions, and more.

You can also invite members on the web application using the traditional invite system or guild referral code. We have also included a command to invite members to your ReadyRaider guild through the Discord bot.

Some useful features:
---------------------

1.  ![interactive connection](https://pbs.twimg.com/profile_images/1270459987714879489/oUEyisT3_400x400.jpg)Links directly to ReadyRaider's Guild Management Web App
2.  ![html cleaner](https://img.icons8.com/fluent/48/000000/checked.png)Pledge attendance to events with reactions
3.  ![Word to html](https://img.icons8.com/fluent/48/000000/today.png)View confirmed event attendance
4.  ![replace text](https://img.icons8.com/fluent/48/000000/knight-shield.png)View past loot information and wish lists
5.  ![gibberish](https://img.icons8.com/fluent/48/000000/armored-breastplate.png)Look up character gear and past performance
6.  ![html table div](https://dmszsuqyoe6y6.cloudfront.net/img/warcraft/favicon.png)Guild Warcraft Logs integration
7.  ![html table div](https://img.icons8.com/fluent/48/000000/invite.png)Invite members to join your guild through Discord
8.  ![html table div](https://img.icons8.com/fluent/48/000000/available-updates.png)Constantly updating to provide more functions

Command Table:
--------------

| ReadyRaider Commands | Description |
| --- | --- |
| $set | Sets the bot up. You need to have an active ReadyRaider Account with Discord Linked! Requires server admin permissions. It should be your first command after inviting the bot. |
| $loot [days=0] | Displays all loot from the day that was X days ago. default = 0 (today). |
| $prio [item name] | Displays recommended class priority for an item (case sensative!) |
| $wishlist [wow name] | Displays wishlist for target character (case sensative!) |
| $upcoming | Updates and displays information about all raids in the upcoming week. |
| $completed | Displays all raids from the last week and the confirmed attendance. |
| $invite [email] [wowName] | Invites a user to join ReadyRaider. Auto-deletes the Post immidiately to hide the email address. |
| $register [email] [wowName] [wowClass] | Register yourself for ReadyRaider. Auto-deletes the post immidiately to hide the email address. |
| $howtouse | Text describing how to use the bot |
| $whatsnew | Displays recent updates |

| WarcraftLogs Commands | Description |
| --- | --- |
| $logs [character name] [server name (Defualts to Registered Server if Blank)]  | Displays rankings for a character. Regions are in the format: US, EU, KR, TW, CN. |
| $gear [character name] [server name (Defualts to Registered Server if Blank)] | Displays the gear worn by a character during their best logs. |
| $guildlogs [guildName (Defualts to Registered Guild if Blank)] [server name (Defualts to Registered Server if Blank)]  | Displays recent logs From a Guild. If guilds are longer then one word, please use quotation marks: "Guild Name" |

| NexusHub Commands | Description |
| --- | --- |


Notes: [] parameters are required unless a default value is shown. If you want to give a parameter with spaces use quotation marks " "
