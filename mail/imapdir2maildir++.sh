#!/usr/bin/env bash

#
# Parameters: set according to your local system settings
#

# Path to the IMAPdir
IMAPdirName="${1}/IMAPdir"

# Path to the new Maildir++ directory
maildirName="../Maildir"

# Name used for the inbox with IMAPdir
inboxName="INBOX"

#
# Below here nothing should need to be adjusted
#

# Initialise some variables and settings
shopt -s dotglob

# loop through all file names according to the pattern in $FILES
cd $IMAPdirName

for file in *; 
do
    # Skip over Maildir++ directories
    if [[ ${file:0:1} = "." && -e ${file}/maildirfolder ]];
    then
        continue
    fi

    if [[ ${file} = "INBOX" ]]; then
        continue;
    fi

    # Skip over non-directory file names
    if [[ ! -d ${file} || -L ${file} ]]; then
        continue
    fi

    # create Maildir++ compliant new folder name
    newFile=${file//\\\\/\\}
    newFile=.$newFile

    echo "Renaming from $(pwd)/${file} to ${maildirName}/${newFile}"

    # rename folder name according to Maildir++ specification & add maildirfolder file
    mv "${file}" "${maildirName}/$newFile"
    touch "${maildirName}/$newFile/maildirfolder"
    chmod 600 "${maildirName}/$newFile/maildirfolder"
done


# Adapt subscriptions file
mv .bincimap-subscribed "${maildirName}/.bincimap-subscribed"
