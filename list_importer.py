#! env python3

# Mastodon list importer
# Imports a CSV file (from the Mastodon export format) into 
# new followers and a new list.
#
#
# Jake Gamage (@gogobonobo@pdx.social on Mastodon)
# Heavily relying on the Mastodon.py documentation

import csv
import re
import argparse
from mastodon import Mastodon
import os.path


def main():
    parser = argparse.ArgumentParser(description='Import a CSV file into a mastodon list.')
    parser.add_argument('-s', '--server', required=True,
                        help='Target server')
    parser.add_argument('-u', '--user', required=True,
                        help='Login name (usually an e-mail address)')
    parser.add_argument('-l', '--list', help="Target list name", required=True)
    parser.add_argument('-i', '--ignore_version_check', action="store_true",
                        help="Ignore the Mastodon server version check (useful for communicating with Mastodon forks like Hometown which may have a differently formatted version string")
    parser.add_argument('-t', '--testing', action="store_true",
                        help="Test mode.  Accounts will not be followed and added to the list, but the list will be created")
    parser.add_argument('csv_input', help="Input CSV file")

    args = parser.parse_args()

    # I'm using the presence of this *_clientcred.secret file to see that the app has been registered on an instance.
    clientcred_secret = f"{args.server}_clientcred.secret"
    if not os.path.exists(clientcred_secret):
        # Register your app! This only needs to be done once. Uncomment the code and substitute in your information.
        client_id, client_secret = Mastodon.create_app(
             'list_importer',
             api_base_url = f'https://{args.server}',
             to_file = clientcred_secret
        )
    else:
        with open(clientcred_secret) as f:
            # Get the client ID out of the clientcred file.  It's the first line.
            client_id = f.readline()
            client_secret = f.readline()


    # Then login. This can be done every time, or use persisted.


    mastodon = Mastodon(client_id = clientcred_secret)

    usercred_secret = f"{args.server}_{args.user}_usercred.secret"
    if not os.path.exists(usercred_secret):
        print(f"Please visit {mastodon.auth_request_url(client_id = client_id)} to log in and receive your access token")
        print("Type access token and hit Enter:") 
        auth_code = str(input())
        mastodon.log_in(
            args.user,
            code = auth_code,
            to_file = usercred_secret,
            redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        )

    # To post, create an actual API instance.
    if args.ignore_version_check:
        version_check_mode = "none"
    else:
        version_check_mode = "created"


    mastodon = Mastodon(access_token = usercred_secret, version_check_mode = version_check_mode)
        
    # Get a list of accounts that we're already following so that we don't request them again.
    already_following_firstpage = mastodon.account_following(id = mastodon.me().id)
    already_following = mastodon.fetch_remaining(already_following_firstpage)
    is_already_following = {}
    for follower in already_following:
        is_already_following[follower['acct']] = follower


    # Open up the CSV of accounts targeting a new list

    # Foreach account in CSV
        # Do I follow them?
        # If no, add them
            # If unsuccessful, skip to next.
        # Now, add them to the list
        
    with open(args.csv_input, newline = '') as csvfile:
        acct_reader = csv.DictReader(csvfile)
        ids_to_add = []
        for line in acct_reader:
            # Let's go through a bunch of nonsense to see if we're already following the user.
            # I'm saving my API calls here by gathering all of the followers above and then looking up locally.
            localized_acct = re.sub(f"@{args.server}$", '', line['Account address'], 1)
            if localized_acct in is_already_following:
                print(f"Already following: {line['Account address']} id: {is_already_following[localized_acct].id}")
                ids_to_add.append(is_already_following[localized_acct].id)
            else:
                print("Not following and attempting to add: ", line['Account address'])
                acct_to_add_search = mastodon.account_search(line['Account address'])
                if len(acct_to_add_search) != 1:
                    print(f"Searching for {line['Account address']} yielded zero or more that one value.  Skipping list add for them")
                else:
                    acct_to_add = acct_to_add_search[0]
                    if args.testing:
                        print("Attempting to add ", acct_to_add.id)
                        ids_to_add.append(acct_to_add.id)
                    else:
                        follow_relationship = mastodon.account_follow(acct_to_add)
                        if follow_relationship.following:
                            print(f"Now following {line['Account address']}")
                            ids_to_add.append(acct_to_add.id)
                        else:
                            if follow_relationship.requested:
                                print(f"Requested to follow {acct_to_add}, but cannot add them to a list until they approve")
        # Now, we should have a list of all the accounts we want to add to the follow list in ids_to_add
        #print(ids_to_add)
        all_lists = mastodon.lists()
        print("Got all lists")
        list_found = False
        for l in all_lists:
            if l.title == args.list:
                print("Found existing list")
                target_list = l
                list_found = True
        if not list_found:
            target_list = mastodon.list_create(args.list)
        id_map = { }
        accounts_already_added_firstpage = mastodon.list_accounts(target_list)
        accounts_already_added = mastodon.fetch_remaining(accounts_already_added_firstpage)
        for acct in accounts_already_added:
            id_map[acct.id] = acct
        new_ids_to_add = [ ]
        for this_id in ids_to_add:
            if not this_id in id_map:
                new_ids_to_add.append(this_id)
        if len(new_ids_to_add) > 0:
            if args.testing:
                print("IDs to add: ", new_ids_to_add)
            else:
                mastodon.list_accounts_add(target_list, new_ids_to_add)
        else:
            print("Cound't find any new ids to add to the list!")


if __name__ == "__main__":
    main()
