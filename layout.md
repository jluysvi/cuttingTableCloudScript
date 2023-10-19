# Program Layout
## History
The scripts need to keep a local history of the amount of cuts that had been done one each day. This history also need to be uploaded to the cloud at least once each day so that it's not lost if the local history is wiped out. The script will upload the history to the company drive file using Microsoft's Graph API. The history will be stored in a csv file because it's universal, easy to manipulate and it's easy to import the data into Excel for analysis.

    1. Listen for the serial values.
    2. Write new values to the history if there are any.
    3. Back the data up to the cloud every minute.
    4. Read old data from the history file for the day when the program starts or create a new entry if there is no data for the day.

## Target Setting
Each day of production has a certain amount of cell boards that need to be produced. That figure needs to be displayed on the displays for the cutters to give everyone an idea of the progress that we are making. The person setting the daily targets needs to decide how much each line will be doing and then send that info to the cutters. The cutters should get the values that they use from a cloud file and then save that value as a local backup to use if an internet connection is not possible. The value can also be set from a python script on the same local network, but is overridden if the network goes back up.

    1. Access the spreadsheet that contains the goals for the day, when the history data is backed up.
    2. Display the target value on the screen.
    3. Write the target value to the history for the day. 
    4. If no connection can be made to the servers for the value, display an error and make it possible for a local script to modify the value.
## Servicing 
A count of the servicing intervals need to be kept for the cutting blade, as well as the soldering bath and needs to give alert the management/technicians somehow.

    1. Store the total number of cuts that the blade has done in the history file and do something when the servicing threshold is reached.
    2. Do the same for the soldering bath.