import json
import os
import re
from datetime import timedelta
from pathlib import Path
from threading import Thread

import dotenv
from nostr_sdk import Client, Timestamp, PublicKey, Tag, Keys, Options, Alphabet

from interfaces.dvmtaskinterface import DVMTaskInterface
from tasks.convert_media import MediaConverter
from utils.admin_utils import AdminConfig
from utils.backend_utils import keep_alive
from utils.definitions import EventDefinitions
from utils.dvmconfig import DVMConfig
from utils.nip89_utils import NIP89Config, check_and_set_d_tag
from utils.nostr_utils import get_event_by_id, check_and_set_private_key
from utils.output_utils import post_process_list_to_users

"""
This File contains a Module to find inactive follows for a user on nostr

Accepted Inputs: None needed
Outputs: A list of users that have been inactive 
Params:  None
"""


class DiscoverInactiveFollows(DVMTaskInterface):
    KIND: int = EventDefinitions.KIND_NIP90_PEOPLE_DISCOVERY
    TASK: str = "inactive-follows"
    FIX_COST: float = 50
    client: Client
    dvm_config: DVMConfig

    def __init__(self, name, dvm_config: DVMConfig, nip89config: NIP89Config,
                 admin_config: AdminConfig = None, options=None):
        super().__init__(name, dvm_config, nip89config, admin_config, options)

    def is_input_supported(self, tags):
        # no input required
        return True

    def create_request_from_nostr_event(self, event, client=None, dvm_config=None):
        self.client = client
        self.dvm_config = dvm_config

        request_form = {"jobID": event.id().to_hex()}

        # default values
        user = event.pubkey().to_hex()
        since_days = 90

        for tag in event.tags():
            if tag.as_vec()[0] == 'param':
                param = tag.as_vec()[1]
                if param == "user":  # check for param type
                    user = tag.as_vec()[2]
                elif param == "since_days":  # check for param type
                    since_days = int(tag.as_vec()[2])

        options = {
            "user": user,
            "since_days": since_days
        }
        request_form['options'] = json.dumps(options)
        return request_form

    def process(self, request_form):
        from nostr_sdk import Filter
        from types import SimpleNamespace
        ns = SimpleNamespace()

        options = DVMTaskInterface.set_options(request_form)
        step = 20

        followers_filter = Filter().author(PublicKey.from_hex(options["user"])).kind(3).limit(1)
        followers = self.client.get_events_of([followers_filter], timedelta(seconds=self.dvm_config.RELAY_TIMEOUT))

        if len(followers) > 0:
            result_list = []
            newest = 0
            best_entry = followers[0]
            for entry in followers:
                if entry.created_at().as_secs() > newest:
                    newest = entry.created_at().as_secs()
                    best_entry = entry

            print(best_entry.as_json())
            followings = []
            ns.dic = {}
            for tag in best_entry.tags():
                if tag.as_vec()[0] == "p":
                    following = tag.as_vec()[1]
                    followings.append(following)
                    ns.dic[following] = "False"
            print("Followings: " + str(len(followings)))

            not_active_since_seconds = int(options["since_days"]) * 24 * 60 * 60
            dif = Timestamp.now().as_secs() - not_active_since_seconds
            not_active_since = Timestamp.from_secs(dif)

            def scanList(users, instance, i, st, notactivesince):
                from nostr_sdk import Filter

                keys = Keys.from_sk_str(self.dvm_config.PRIVATE_KEY)
                opts = Options().wait_for_send(True).send_timeout(
                    timedelta(seconds=10)).skip_disconnected_relays(False)
                cli = Client.with_opts(keys, opts)
                for relay in self.dvm_config.RELAY_LIST:
                    cli.add_relay(relay)
                cli.connect()

                filters = []
                for i in range(i + st):
                    filter1 = Filter().author(PublicKey.from_hex(users[i])).since(notactivesince).limit(1)
                    filters.append(filter1)
                event_from_authors = cli.get_events_of(filters, timedelta(seconds=10))
                for author in event_from_authors:
                    instance.dic[author.pubkey().to_hex()] = "True"
                print(str(i) + "/" + str(len(users)))
                cli.disconnect()

            threads = []
            begin = 0
            # Spawn some threads to speed things up
            while begin < len(followings) - step:
                args = [followings, ns, begin, step, not_active_since]
                t = Thread(target=scanList, args=args)
                threads.append(t)
                begin = begin + step

            # last to step size
            missing_scans = (len(followings) - begin)
            args = [followings, ns, begin, missing_scans, not_active_since]
            t = Thread(target=scanList, args=args)
            threads.append(t)

            # Start all threads
            for x in threads:
                x.start()

            # Wait for all of them to finish
            for x in threads:
                x.join()

            result = {k for (k, v) in ns.dic.items() if v == "False"}

            if len(result) == 0:
                print("Not found")
                return "No inactive followers found on relays."
            print("Inactive accounts found: " + str(len(result)))
            for k in result:
                p_tag = Tag.parse(["p", k])
                result_list.append(p_tag.as_vec())

            return json.dumps(result_list)

    def post_process(self, result, event):
        """Overwrite the interface function to return a social client readable format, if requested"""
        for tag in event.tags():
            if tag.as_vec()[0] == 'output':
                format = tag.as_vec()[1]
                if format == "text/plain":  # check for output type
                    result = post_process_list_to_users(result)

        # if not text/plain, don't post-process
        return result

# We build an example here that we can call by either calling this file directly from the main directory,
# or by adding it to our playground. You can call the example and adjust it to your needs or redefine it in the
# playground or elsewhere
def build_example(name, identifier, admin_config):
    dvm_config = DVMConfig()
    dvm_config.PRIVATE_KEY = check_and_set_private_key(identifier)
    dvm_config.LNBITS_INVOICE_KEY = os.getenv("LNBITS_INVOICE_KEY")
    dvm_config.LNBITS_URL = os.getenv("LNBITS_HOST")
    # Add NIP89
    nip90params = {
        "user": {
            "required": False,
            "values": [],
            "description": "Do the task for another user"
        },
        "since_days": {
            "required": False,
            "values": [],
            "description": "The number of days a user has not been active to be considered inactive"

        }
    }
    nip89info = {
        "name": name,
        "image": "https://image.nostr.build/c33ca6fc4cc038ca4adb46fdfdfda34951656f87ee364ef59095bae1495ce669.jpg",
        "about": "I discover users you follow, but that have been inactive on Nostr",
        "encryptionSupported": True,
        "cashuAccepted": True,
        "nip90Params": nip90params
    }

    nip89config = NIP89Config()
    nip89config.DTAG = check_and_set_d_tag(identifier, name, dvm_config.PRIVATE_KEY,
                                                              nip89info["image"])

    nip89config.CONTENT = json.dumps(nip89info)
    return DiscoverInactiveFollows(name=name, dvm_config=dvm_config, nip89config=nip89config,
                                   admin_config=admin_config)


if __name__ == '__main__':
    env_path = Path('.env')
    if env_path.is_file():
        print(f'loading environment from {env_path.resolve()}')
        dotenv.load_dotenv(env_path, verbose=True, override=True)
    else:
        raise FileNotFoundError(f'.env file not found at {env_path} ')

    admin_config = AdminConfig()
    admin_config.REBROADCAST_NIP89 = False
    admin_config.UPDATE_PROFILE = False
    admin_config.LUD16 = ""

    dvm = build_example("Bygones", "discovery_inactive_follows", admin_config)
    dvm.run()

    keep_alive()