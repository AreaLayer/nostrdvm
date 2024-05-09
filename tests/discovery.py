import os
import threading
from pathlib import Path

import dotenv
from nostr_sdk import Keys

from nostr_dvm.subscription import Subscription
from nostr_dvm.tasks import content_discovery_currently_popular, content_discovery_currently_popular_topic
from nostr_dvm.utils.admin_utils import AdminConfig
from nostr_dvm.utils.backend_utils import keep_alive
from nostr_dvm.utils.dvmconfig import DVMConfig
from nostr_dvm.utils.nostr_utils import check_and_set_private_key
from nostr_dvm.utils.zap_utils import check_and_set_ln_bits_keys


def playground():
    # Generate an optional Admin Config, in this case, whenever we give our DVMs this config, they will (re)broadcast
    # their NIP89 announcement
    # You can create individual admins configs and hand them over when initializing the dvm,
    # for example to whilelist users or add to their balance.
    # If you use this global config, options will be set for all dvms that use it.
    admin_config = AdminConfig()
    admin_config.REBROADCAST_NIP89 = False
    admin_config.UPDATE_PROFILE = False
    # admin_config.DELETE_NIP89 = True
    # admin_config.PRIVKEY = ""
    # admin_config.EVENTID = ""

    # discovery_test_sub = content_discovery_currently_popular.build_example_subscription("Currently Popular Notes DVM (with Subscriptions)", "discovery_content_test", admin_config)
    # discovery_test_sub.run()

    options_plants = {
        "search_list": ["garden", "gardening", "nature", " plants ", " plant ", " herb ", " herbs " " pine ",
                        "homesteading", "rosemary", "chicken", "🪻", "🌿", "☘️", "🌲", "flower", "forest", "watering",
                        "permies", "planting", "farm", "vegetable", "fruit",  " grass ", "sunshine",
                        "#flowerstr", "#bloomscrolling", "#treestr", "#plantstr"],
         "avoid_list": ["porn", "smoke", "nsfw", "bitcoin", "bolt12", "bolt11", "github", "currency", "utxo",
                       "encryption", "government", "airpod", "ipad", "iphone", "android", "warren",
                       "moderna", "pfizer",
                       "murder", "tax", "engagement", "hodlers", "hodl", "gdp", "global markets", "crypto", "wherostr",
                       "presidency", "dollar", "asset", "microsoft", "amazon", "billionaire", "ceo", "industry",
                       "white house", "blocks", "streaming", "summary", "wealth", "beef", "cunt", "nigger", "business",
                       "retail", "bakery", "synth", "slaughterhouse", "hamas", "dog days", "ww3", "socialmedia",
                       "nintendo", "signature", "deepfake", "congressman", "cypherpunk", "minister", "dissentwatch",
                        "inkblot", "covid", "robot", "pandemic",  "bethesda", "zap farming", " defi ", " minister ",
                        "nostr-hotter-site", " ai ", "palestine", "https://boards.4chan", "https://techcrunch.com", "https://screenrant.com"],
        "db_name": "db/nostr_recent_notes_plants.db",
        "db_since": 10 * 60 * 60}  # 10h

    image = "https://image.nostr.build/a816f3f5e98e91e8a47d50f4cd7a2c17545f556d9bb0a6086a659b9abdf7ab68.jpg"
    description = "I show recent notes about plants and gardening"
    discovery_test_sub = content_discovery_currently_popular_topic.build_example("Garden & Growth",
                                                                                 "discovery_content_garden",
                                                                                 admin_config, options_plants, image,
                                                                                 description)
    discovery_test_sub.run()

    options_animal = {
        "search_list": ["catstr", "pawstr", "dogstr", " cat ", " cats ", "🐾", "🐈", "🐕" , " dog ", " dogs ", " fluffy ", "animal",
                        " duck", " lion ", " lions ", " fox ", " foxes ", " koala ", " koalas ", "capybara", "squirrel", "monkey", "panda", "alpaca", " otter"],
        "avoid_list": ["porn", "smoke", "nsfw", "bitcoin", "bolt12", "bolt11", "github", "currency", "utxo",
                       "encryption", "government", "airpod", "ipad", "iphone", "android", "warren",
                       "moderna", "pfizer",
                       "murder", "tax", "engagement", "hodlers", "hodl", "gdp", "global markets", "crypto", "wherostr",
                       "presidency", "dollar", "asset", "microsoft", "amazon", "billionaire", "ceo", "industry",
                       "white house", "blocks", "streaming", "summary", "wealth", "beef", "cunt", "nigger", "business",
                       "retail", "bakery", "synth", "slaughterhouse", "hamas", "dog days", "ww3", "socialmedia",
                       "nintendo", "signature", "deepfake", "congressman", "fried chicken", "cypherpunk",
                       "chef", "cooked", "foodstr", "minister", "dissentwatch", "inkblot", "covid", "robot", "pandemic",
                       " dies ", "bethesda", " defi ", " minister ", "nostr-hotter-site", " ai ", "palestine", " hit by a", "https://boards.4chan", "https://techcrunch.com", "https://screenrant.com"],


    "must_list": ["http"],
        "db_name": "db/nostr_recent_notes_animals.db",
        "db_since": 48 * 60 * 60}  # 10h

    image = "https://image.nostr.build/f609311532c470f663e129510a76c9a1912ae9bc4aaaf058e5ba21cfb512c88e.jpg"
    description = "I show recent notes about animals"
    discovery_test_sub2 = content_discovery_currently_popular_topic.build_example("Fluffy Frens",
                                                                                  "discovery_content_fluffy",
                                                                                  admin_config, options_animal, image,
                                                                                  description)
    discovery_test_sub2.run()

    # discovery_test = content_discovery_currently_popular.build_example("Currently Popular Notes DVM",
    #                                                                   "discovery_content_test", admin_config)
    # discovery_test.run()

    subscription_config = DVMConfig()
    subscription_config.PRIVATE_KEY = check_and_set_private_key("dvm_subscription")
    npub = Keys.parse(subscription_config.PRIVATE_KEY).public_key().to_bech32()
    invoice_key, admin_key, wallet_id, user_id, lnaddress = check_and_set_ln_bits_keys("dvm_subscription", npub)
    subscription_config.LNBITS_INVOICE_KEY = invoice_key
    subscription_config.LNBITS_ADMIN_KEY = admin_key  # The dvm might pay failed jobs back
    subscription_config.LNBITS_URL = os.getenv("LNBITS_HOST")
    sub_admin_config = AdminConfig()
    # sub_admin_config.USERNPUBS = ["7782f93c5762538e1f7ccc5af83cd8018a528b9cd965048386ca1b75335f24c6"] #Add npubs of services that can contact the subscription handler
    # x = threading.Thread(target=Subscription, args=(Subscription(subscription_config, sub_admin_config),))
    # x.start()

    # keep_alive()


if __name__ == '__main__':
    env_path = Path('.env')
    if not env_path.is_file():
        with open('.env', 'w') as f:
            print("Writing new .env file")
            f.write('')
    if env_path.is_file():
        print(f'loading environment from {env_path.resolve()}')
        dotenv.load_dotenv(env_path, verbose=True, override=True)
    else:
        raise FileNotFoundError(f'.env file not found at {env_path} ')
    playground()
